from app.models import CartTable, ProductTable, PurchaseHistory
from app.auth.permission import is_user
from app.auth.OAuth2 import get_current_user
from sqlalchemy.orm import Session
from app.connection import get_db
from fastapi import HTTPException, APIRouter, Depends, Query
from app.schema.user_schema import (
    CreateCart, CartResponse, RemoveCartList,
    UpdateCartQtyList, CartDisplayResponse, PurchaseHistoryData,
    PurchaseOut
)
from app.schema.common_schema import MessageOut
from typing import List
from sqlalchemy import func
from app.Repository.product_repo import get_product_byname
from app.Logger.logger import logger
from app.utils import paginate_query

# RBAC - User control routes
router = APIRouter(
    prefix="/user",
    tags=["User"]
)

# Adding items to the cart by the user
@router.post("/createcart", response_model=List[CartResponse])
def create_cart(cart: CreateCart, db: Session = Depends(get_db), user=Depends(get_current_user)):
    logger.info(f"User {user.user_id} adding items to cart")
    try:
        cart_items = []
        for item in cart.cart_value:   
            product = get_product_byname(db, item.product_name)
            if item.quantity > product.product_stockqty:
                raise HTTPException(status_code=422, detail=f"Insufficient stock for '{item.product_name}'. Available quantity : {product.product_stockqty}")

            new_cart_item = CartTable(
                quantity=item.quantity,
                user_id=user.user_id,          
                product_id=product.product_id, 
               )
            db.add(new_cart_item)
            product.product_stockqty -= item.quantity
            cart_items.append(new_cart_item)

        db.commit()
        for item in cart_items:
            db.refresh(item)
        logger.info(f"Items added to the cart by User {user.user_id}")
        response_data = []
        for item in cart_items:
            response_data.append({
                "cart_id": item.cart_id,
                "user_id": item.user_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product_name": item.product.product_name
            })

        return response_data
    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error while adding cart: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User Removing items from the cart
@router.delete("/remove_item", response_model=MessageOut)
def remove_cart_item(data: RemoveCartList, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logger.info(f"User {current_user.user_id} trying to remove product from the cart")
    try:
        for item in data.remove_cart:
            product = get_product_byname(db, item.product_name)
            remove_item = db.query(CartTable).filter(
                CartTable.user_id == current_user.user_id,
                CartTable.product_id == product.product_id
            ).first()
            if not remove_item:
                raise HTTPException(status_code=404, detail=f"'{item.product_name}' not found in your cart")

            product.product_stockqty += remove_item.quantity
            db.delete(remove_item)

        db.commit()
        logger.info(f"User {current_user.user_id} removed {len(data.remove_cart)} selected items from the cart")
        return {"message": "Selected items removed from cart successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error while removing items from the cart: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User Updating cart quantity
@router.patch("/updatecartquantity", response_model=MessageOut)
def update_cartquantity(data: UpdateCartQtyList, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logger.info(f"User {current_user.user_id} wants to update cart quantity")
    try:
        for item in data.new_cartqty:
            product = get_product_byname(db, item.product_name)
            update_qtyitem = db.query(CartTable).filter(
                CartTable.user_id == current_user.user_id,
                CartTable.product_id == product.product_id
            ).first()
            if not update_qtyitem:
                raise HTTPException(status_code=404, detail=f"'{item.product_name}' not found in your cart")

            old_qty = update_qtyitem.quantity
            update_qtyitem.quantity = item.new_quantity

            # Adjust stock
            if item.new_quantity < old_qty:
                product.product_stockqty += (old_qty - item.new_quantity)
            else:
                product.product_stockqty -= (item.new_quantity - old_qty)

        db.commit()
        logger.info(f"User {current_user.user_id} updated {len(data.new_cartqty)} cart quantity")
        return {"message": "Cart item quantity updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error while updating cart quantity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Display the list of cart items
@router.get("/displaycartitems", response_model=CartDisplayResponse)
def display_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user),
                 page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    logger.info(f"Displaying the cart items to the user {current_user.user_id}")
    try:
        cart_query = (
            db.query(CartTable, ProductTable)
            .join(ProductTable, CartTable.product_id == ProductTable.product_id)
            .filter(CartTable.user_id == current_user.user_id)
        )
        cart_records = paginate_query(cart_query, page, limit)
        if not cart_records:
            print("Cart is empty")

        cart_items = []
        total_cart_value = 0.0

        for cart, product in cart_records:
            total_price = cart.quantity * product.product_price
            total_cart_value += total_price
            cart_items.append({
                "product_id": product.product_id,
                "product_name": product.product_name,
                "quantity": cart.quantity,
                "price_per_item": product.product_price,
                "total_price": total_price
            })
        logger.info("Cart items displayed")
        return {
            "cart_items": cart_items,
            "total_cart_value": total_cart_value
        }
    except Exception:
        db.rollback()
        #logger.error(f"Error while displaying cart items: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Checking out the cart items added by the user
@router.get("/cartcheckout")
def cart_checkout(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logger.info(f"Checking out the cart items added by the user {current_user.user_id}")
    try:
        cart_items = db.query(CartTable, ProductTable).join(
            ProductTable, CartTable.product_id == ProductTable.product_id
        ).filter(CartTable.user_id == current_user.user_id).all()

        if not cart_items:
            raise HTTPException(status_code=404, detail="Cart is empty")

        for cart, product in cart_items:
            new_purchase = PurchaseHistory(
                user_id=current_user.user_id,
                product_id=product.product_id,
                quantity=cart.quantity,
                total_price=cart.quantity * product.product_price
            )
            db.add(new_purchase)

        db.query(CartTable).filter(CartTable.user_id == current_user.user_id).delete()
        db.commit()

        return {"message": "Checkout completed successfully"}

    except Exception as e:
        db.rollback()
        logger.error(f"Checkout failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Displaying the purchase history of the user
@router.post("/displaypurchasehistory", response_model=List[PurchaseOut])
def display_purchasehistory(data: PurchaseHistoryData, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logger.info(f"Displaying the purchase history of the user {current_user.user_id}")
    try:
        user_id = current_user.user_id if current_user.user_role == "user" else data.user_id or current_user.user_id
        query = db.query(PurchaseHistory).filter(PurchaseHistory.user_id == user_id)
        if data.date:
            query = query.filter(func.date(PurchaseHistory.purchase_date) == data.date)

        cart_purchasehistory = query.all()
       
        if not cart_purchasehistory:
            raise HTTPException(status_code=404, detail="No purchase history found")

        logger.info(f"Purchase history of the user {current_user.user_id} is displayed")
        return cart_purchasehistory
    except HTTPException:
        
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error while displaying purchase history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
