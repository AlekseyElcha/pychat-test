from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    is_admin: Mapped[bool]
    is_banned: Mapped[bool]

class UserSchema(BaseModel):
    id: int
    username: str
    login: EmailStr
    password: str
    is_admin: bool
    is_banned: bool

class UserAddSchema(BaseModel):
    username: str
    login: EmailStr
    password: str = Field(min_length=6)
    is_admin: bool = False
    is_banned: bool = False


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(default=UserModel.username)
    login: Optional[EmailStr] = Field(default=UserModel.login)
    password: Optional[str] = Field(default=UserModel.password)

class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    content: Mapped[str]

class MessageSchema(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    time: datetime
    content: str

class MessageCreateSchema(BaseModel):
    recipient_id: int
    content: str