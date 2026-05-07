from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

def get_all_orders(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def get_order_by_id(order_id: int, user_id: int, db: Session):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user_id
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    return order

def create_order(order: schemas.OrderCreate, user_id: int, db: Session):
    product = db.query(models.Product).filter(
        models.Product.id == order.product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {order.product_id} not found"
        )
    if product.stock < order.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock. Available: {product.stock}"
        )
    if order.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero"
        )
    total_price = product.price * order.quantity
    product.stock -= order.quantity
    db_order = models.Order(
        quantity=order.quantity,
        total_price=total_price,
        user_id=user_id,
        product_id=order.product_id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order(order_id: int, user_id: int, db: Session):
    db_order = get_order_by_id(order_id, user_id, db)
    product = db.query(models.Product).filter(
        models.Product.id == db_order.product_id
    ).first()
    if product:
        product.stock += db_order.quantity
    db.delete(db_order)
    db.commit()
    return {"message": f"Order {order_id} cancelled successfully"}