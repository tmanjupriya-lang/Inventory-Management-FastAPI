from pydantic import BaseModel, Field, field_validator

class ProductInfo(BaseModel):
    product_name: str = Field(min_length=1, max_length=100, pattern="^[A-Za-z0-9 ]+$", description="Name of the product")
    product_stockqty: int = Field(gt=0, description="Number of items in stock", example=20)
    product_price: float = Field(gt=0, description="Price per unit", example=199.99)

    @field_validator("product_name")
    def name_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Product name cannot be blank or spaces only")
        return v

class RemoveProduct(BaseModel):
    product_id: int

class UpdatePrice(BaseModel):
    product_id: int
    new_price: float = Field(gt=0)

class UpdateStockQty(BaseModel):
    product_id: int
    update_qty: int = Field(gt=0)

class ProductOut(BaseModel):
    product_id: int
    product_name: str
    product_stockqty: int
    product_price: float

