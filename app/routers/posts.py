from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.auth.dependencies import get_current_active_user

router = APIRouter(tags=["posts"])

@router.post("/topics/{topic_id}/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(
    topic_id: int,
    post_data: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
   
    new_post = models.Post(
        content=post_data.content,
        topic_id=topic_id,
        author_id=current_user.id
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return schemas.PostResponse(
        id=new_post.id,
        content=new_post.content,
        topic_id=new_post.topic_id,
        author_id=new_post.author_id,
        author_username=current_user.username,
        created_at=new_post.created_at
    )
