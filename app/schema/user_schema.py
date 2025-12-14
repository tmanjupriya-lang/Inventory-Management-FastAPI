from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class Cart(BaseModel):
    product_id: int
    product_name: str
    quantity: int = 1

class CreateCart(BaseModel):
    cart_value: List[Cart]


class CartItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price_per_item: float
    total_price: float

    class Config:
        orm_mode = True

class CartDisplayResponse(BaseModel):
    cart_items: List[CartItemOut]
    total_cart_value: float

class ProductInCart(BaseModel):
    product_id: int
    product_name: str
    quantity: int = 1

    class Config:
        orm_mode = True

class CartResponse(BaseModel):
    cart_id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: str  

    class Config:
        orm_mode = True

class RemoveCart(BaseModel):
    product_id: int
    product_name: str
    quantity: int

class RemoveCartList(BaseModel):
    remove_cart: List[RemoveCart]

class UpdateCartQuantity(BaseModel):
    product_id: int
    product_name: str
    new_quantity: int = Field(gt=0)

class UpdateCartQtyList(BaseModel):
    new_cartqty: List[UpdateCartQuantity]

class PurchaseHistoryData(BaseModel):
    user_id: int
    date: datetime

class PurchaseOut(BaseModel):
    purchase_id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    purchase_date: datetime

    class Config:
        orm_mode = True
