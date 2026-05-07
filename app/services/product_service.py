from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

def get_all_products(db: Session):
    return db.query(models.Product).all()

def get_product_by_id(product_id: int, db: Session):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return product

def create_product(product: schemas.ProductCreate, db: Session):
    if product.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than zero"
        )
    if product.stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock cannot be negative"
        )
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(product_id: int, product: schemas.ProductUpdate, db: Session):
    db_product = get_product_by_id(product_id, db)
    update_data = product.model_dump(exclude_unset=True)
    if "price" in update_data and update_data["price"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than zero"
        )
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(product_id: int, db: Session):
    db_product = get_product_by_id(product_id, db)
    db.delete(db_product)
    db.commit()
    return {"message": f"Product {product_id} deleted successfully"}