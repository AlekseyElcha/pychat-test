import os
from sqlalchemy import select
from fastapi import Depends, HTTPException, Response, APIRouter
from authx import AuthXConfig, AuthX
from dotenv import load_dotenv
from typing import Dict, Any
from datetime import datetime

from schemas.schemas import UserModel, UserAddSchema
from database.database import SessionDep

router = APIRouter(prefix="/auth")

load_dotenv()
config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
config.JWT_TOKEN_LOCATION = ["cookies", "headers"]
config.JWT_ALGORITHM = "HS256"
config.JWT_COOKIE_CSRF_PROTECT = False
security = AuthX(config=config)

@router.post("/login")
async def login(login: str, password: str, response: Response = None, session: SessionDep = None):
    query = select(UserModel).where(UserModel.login == login).where(UserModel.password == password)
    result = await session.execute(query)
    data = result.scalars_one_or_none()
    if data:
        is_admin = int(data.is_admin)
        is_adm = 1 if is_admin else 0
        user_data = {
            "login": data.login,
            "is_admin": is_adm
        }
        token = security.create_access_token(uid=login, data=user_data)
        security.set_access_cookies(token, response)

        return {
            "success": True,
            "access_token": token,
            "user": {
                "id": data.id,
                "login": data.login,
                "username": data.username,
                "is_admin": bool(data.is_admin)
            }
        }
    raise HTTPException(status_code=404, detail="Неверный логин или пароль")


@router.post("/create_account")
async def create_account(user: UserAddSchema, session: SessionDep):
    try:
        new_user = UserModel(
            login=user.login,
            username=user.username,
            is_admin=user.is_admin,
            password=user.password,
            is_banned=user.is_banned,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при создании аккаунта")
    return {
        "new_user": {
            "id": new_user.id,
            "login": new_user.login,
            "username": new_user.username,
            "is_admin": new_user.is_admin,
            "is_banned": new_user.is_banned,
        },
        "message": "Аккаунт успешно создан!"
    }


async def admin_required(user = Depends(security.access_token_required)):
    try:
        is_admin = user.get("is_admin")
    except AttributeError:
        is_admin = getattr(user, 'is_admin', False)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user



