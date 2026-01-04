from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, or_, and_
from datetime import datetime
import jwt
import os

from authorization.auth import admin_required, security, check_user
from database.database import SessionDep, engine
from schemas.schemas import UserModel, MessageModel

router = APIRouter(prefix="/ops")
secret = os.getenv("JWT_SECRET_KEY")

@router.get("/user_info/{user_id}", dependencies=[Depends(security.access_token_required)])
async def get_user_info(user_id: int, session: SessionDep):
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user_info = result.scalar_one_or_none()
        if user_info is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return {
            "success": True,
            "user_info": user_info
        }

@router.post("/send_message", dependencies=[Depends(security.access_token_required)])
async def send_message(sender_id: int, recipient_id: int, content: str, session: SessionDep):
    try:
        new_message = MessageModel(
        sender_id=sender_id,
        recipient_id=recipient_id,
        time=datetime.utcnow(),
        content=content,
        )
        session.add(new_message)
        await session.commit()
        await session.refresh(new_message)

        return {
            "success": True,
            "new_message": {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "content": content
            }
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при отправке сообщения")

@router.get("/get_messages", dependencies=[Depends(security.access_token_required)])
async def get_chat_history(user_id: int, partner_id: int, session: SessionDep, request: Request):
    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    user_info = result.scalar_one_or_none()
    return user_info.json()
    # token = request.cookies["auth_cookies"]
    # t = check_user(auth_token=token, expected_login=user_login)
    # return t
    # query = select(MessageModel).where(
    # or_(
    #     and_(
    #         MessageModel.sender_id == user_id,
    #         MessageModel.recipient_id == partner_id,
    #     ),
    #     and_(
    #         MessageModel.sender_id == partner_id,
    #         MessageModel.recipient_id == user_id,
    #     )
    # )
    # )
    # result = await session.execute(query)
    # messages = result.scalars().all()
    # if messages is None:
    #     raise HTTPException(status_code=404, detail="Сообщения не найдены")
    # return messages

