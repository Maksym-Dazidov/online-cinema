from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.crud.order import order_crud
from app.schemas.order import OrderRead

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/from-cart", response_model=OrderRead)
async def create_order_from_cart(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    return await order_crud.create_from_cart(db, current_user.id)


@router.get("", response_model=list[OrderRead])
async def list_my_orders(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    return await order_crud.get_for_user(db, current_user.id)


@router.get("/{order_id}", response_model=OrderRead)
async def get_my_order(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    order = await order_crud.get_by_id_for_user(db, current_user.id, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_my_order(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    return await order_crud.cancel(db, current_user.id, order_id)
