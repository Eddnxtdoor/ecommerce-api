from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import get_current_user
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=list[schemas.OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return order_service.get_all_orders(db, current_user.id)

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return order_service.get_order_by_id(order_id, current_user.id, db)

@router.post("/", response_model=schemas.OrderResponse, status_code=201)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return order_service.create_order(order, current_user.id, db)

@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return order_service.delete_order(order_id, current_user.id, db)