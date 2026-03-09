from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List
import sys

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)  # Добавлено явное ограничение
    
    @validator('password')
    def validate_password_length(cls, v):
        """Проверка длины пароля"""
        # Проверяем длину в байтах
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            error_msg = f"Password too long: {len(password_bytes)} bytes (max 72 bytes). Please use a shorter password."
            print(error_msg)
            raise ValueError(error_msg)
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# Topic schemas
class TopicBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    author_id: int
    author_username: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    
    class Config:
        from_attributes = True

class TopicDetailResponse(TopicBase):
    id: int
    author_id: int
    author_username: str
    created_at: datetime
    updated_at: datetime
    posts: List["PostResponse"] = []
    
    class Config:
        from_attributes = True

# Post schemas
class PostBase(BaseModel):
    content: str = Field(..., min_length=1)

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    topic_id: int
    author_id: int
    author_username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Обновление forward references
TopicDetailResponse.model_rebuild()