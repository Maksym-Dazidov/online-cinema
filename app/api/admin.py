from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_admin
from app.db.session import get_db
from app.crud.user import user_crud
from app.crud.user_group import user_group_crud
from app.schemas.user_group import UserGroupRead

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/groups", response_model=list[UserGroupRead], dependencies=[Depends(require_admin)])
async def list_groups(
    db: AsyncSession = Depends(get_db),
):
    return await user_group_crud.get_multi(db)


@router.post("/set-role/{user_id}/{role_name}", dependencies=[Depends(require_admin)])
async def set_role(
    user_id: int,
    role_name: str,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    group = await user_group_crud.get_by_name(db, role_name)
    if not group:
        raise HTTPException(status_code=404, detail="Role not found")

    user.group_id = group.id
    await db.commit()
    await db.refresh(user)

    return {
        "message": f"User {user.email} is now {role_name}",
        "user_id": user.id,
        "role": role_name,
    }


@router.post("/set-admin/{user_id}", dependencies=[Depends(require_admin)])
async def set_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    admin_group = await user_group_crud.get_by_name(db, "admin")
    user.group_id = admin_group.id

    await db.commit()
    await db.refresh(user)

    return {"message": f"User {user.email} is now admin"}
