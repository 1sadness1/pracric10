from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app import models, schemas
from app.database import get_db
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/topics", tags=["topics"])

@router.get("/", response_model=List[schemas.TopicResponse])
def get_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получение списка всех тем"""
    # Получаем темы с количеством сообщений
    topics = db.query(
        models.Topic,
        func.count(models.Post.id).label("message_count")
    ).outerjoin(
        models.Post, models.Post.topic_id == models.Topic.id
    ).group_by(
        models.Topic.id
    ).order_by(
        models.Topic.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for topic, message_count in topics:
        result.append(schemas.TopicResponse(
            id=topic.id,
            title=topic.title,
            content=topic.content,
            author_id=topic.author_id,
            author_username=topic.author.username,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
            message_count=message_count
        ))
    
    return result

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TopicResponse)
def create_topic(
    topic_data: schemas.TopicCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Создание новой темы"""
    new_topic = models.Topic(
        title=topic_data.title,
        content=topic_data.content,
        author_id=current_user.id
    )
    
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    
    return schemas.TopicResponse(
        id=new_topic.id,
        title=new_topic.title,
        content=new_topic.content,
        author_id=new_topic.author_id,
        author_username=current_user.username,
        created_at=new_topic.created_at,
        updated_at=new_topic.updated_at,
        message_count=0
    )

@router.get("/{topic_id}", response_model=schemas.TopicDetailResponse)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db)
):
    """Получение темы со всеми сообщениями"""
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Получаем все сообщения темы
    posts = db.query(models.Post).filter(
        models.Post.topic_id == topic_id
    ).order_by(
        models.Post.created_at.asc()
    ).all()
    
    # Формируем список сообщений
    posts_data = []
    for post in posts:
        posts_data.append(schemas.PostResponse(
            id=post.id,
            content=post.content,
            topic_id=post.topic_id,
            author_id=post.author_id,
            author_username=post.author.username,
            created_at=post.created_at
        ))
    
    return schemas.TopicDetailResponse(
        id=topic.id,
        title=topic.title,
        content=topic.content,
        author_id=topic.author_id,
        author_username=topic.author.username,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        posts=posts_data
    )