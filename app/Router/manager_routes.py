from app.models import ProductTable
from sqlalchemy.orm import Session
from app.connection import get_db
from typing import List
from fastapi import status, HTTPException, APIRouter, Depends, Query
from app.schema.manager_schema import (
    ProductInfo, ProductOut, RemoveProduct,
    UpdatePrice, UpdateStockQty
)
from app.schema.common_schema import MessageOut
from app.auth.permission import is_inventorymanager
from sqlalchemy.exc import IntegrityError
from app.Repository.product_repo import get_product_byid
from app.Logger.logger import logger
from app.utils import paginate_query

# RBAC - Manager control routes
router = APIRouter(
    prefix="/manager",
    tags=["Inventory Manager"]
)

# Adding products info to the Product table in the database
@router.post("/create-product", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def add_product(
    data: ProductInfo,
    db: Session = Depends(get_db),
    current_user=Depends(is_inventorymanager)
):
    logger.info(f"Inventory Manager {current_user.user_id} is adding a new product")

    try:
        # Check if product with same name already exists
        existing_product = db.query(ProductTable).filter(ProductTable.product_name == data.product_name).first()

        if existing_product:
            raise HTTPException(status_code=409,detail="Product name already exists. Please choose a different name.")

        new_product = ProductTable(
            product_name=data.product_name,
            product_price=data.product_price,
            product_stockqty=data.product_stockqty
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        logger.info(f"Product '{new_product.product_name}' added successfully by Inventory Manager {current_user.user_id}")

        return new_product

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error while adding product: {e}")
        raise HTTPException(status_code=500,detail="Internal server error")
    
# Removing products from the Product table
@router.delete("/remove-product", response_model=MessageOut)
def remove_product(data: RemoveProduct, db: Session = Depends(get_db), current_user=Depends(is_inventorymanager)):
    logger.info(f"Inventory Manager {current_user.user_id} removing product {data.product_id}")
    try:
        product = get_product_byid(db, data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        db.delete(product)
        db.commit()
        logger.info(f"Product {data.product_id} removed by Inventory Manager {current_user.user_id}")
        return {"message": f"Product ID {data.product_id} removed successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error while removing product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Updating stock quantity of the product
@router.patch("/update-stockqty", response_model=MessageOut)
def update_stockqty(data: UpdateStockQty, db: Session = Depends(get_db), current_user=Depends(is_inventorymanager)):
    logger.info(f"Inventory Manager {current_user.user_id} updating stock for product {data.product_id}")
    try:
        product = get_product_byid(db, data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.product_stockqty += data.update_qty
        db.commit()
        db.refresh(product)
        logger.info(f"Stock updated for product {data.product_id} by Inventory Manager {current_user.user_id}")
        return {"message": f"Stock quantity for Product {data.product_id} updated successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error while updating stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Updating the price of the product
@router.patch("/update-price", response_model=MessageOut)
def update_price(data: UpdatePrice, db: Session = Depends(get_db), current_user=Depends(is_inventorymanager)):
    logger.info(f"Inventory Manager {current_user.user_id} updating price for product {data.product_id}")
    try:
        product = get_product_byid(db, data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.product_price = data.new_price
        db.commit()
        db.refresh(product)
        logger.info(f"Price updated for product {data.product_id} by Inventory Manager {current_user.user_id}")
        return {"message": f"Price for Product {data.product_id} updated successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error while updating price: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# Viewing all products
@router.get("/view-products", response_model=List[ProductOut])
def view_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100), current_user=Depends(is_inventorymanager)
):
    print(current_user)
    logger.info(f"Inventory Manager viewing products - Page {page}, Limit {limit}")
    query = db.query(ProductTable)
    products = paginate_query(query, page, limit)
    if not products:
        logger.info("No products found")
        raise HTTPException(status_code=404, detail="No products found")
        
    return products
