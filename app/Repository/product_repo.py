from app.models import ProductTable
from fastapi import HTTPException

def get_product_byname(db, product_name:str):
    product = db.query(ProductTable).filter(ProductTable.product_name == product_name).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found")
    return product

def get_product_byid(db,product_id:int):
    product = db.query(ProductTable).filter(ProductTable.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail= "Product not found")
    return product