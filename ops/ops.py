from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from authorization.auth import admin_required, security
from database.database import SessionDep, engine
from schemas.schemas import UserModel

router = APIRouter(prefix="/ops")

@router.get("/user_info/{user_id}", dependencies=[Depends(security.access_token_required)])
async def get_user_info(user_id: int, session: SessionDep):
    try:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user_info = result.scalar_one_or_none()
        if user_info is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return {
            "success": True,
            "user_info": user_info
        }
    except:
        raise HTTPException(status_code=403, detail="Нет доступа")