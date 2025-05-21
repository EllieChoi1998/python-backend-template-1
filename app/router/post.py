from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from models import get_db
from service.post import PostService
from auth.jwt_bearer import JWTBearer, get_current_user_id
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/posts", tags=["Posts"])

# 요청 및 응답 모델
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)

class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    view_count: int
    created_at: str
    modified_at: str
    author_name: Optional[str] = None

# 라우트 정의
@router.get("/", response_model=List[PostResponse])
def get_posts(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """모든 게시물 조회"""
    post_service = PostService(db)
    return post_service.get_all_posts(limit, offset)

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """특정 게시물 조회 (조회수 증가)"""
    post_service = PostService(db)
    return post_service.get_post_by_id(post_id, increment_views=True)

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: PostCreate, 
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user_id)
):
    """새 게시물 작성 (인증 필요)"""
    post_service = PostService(db)
    return post_service.create_post(post.dict(), current_user_id)

@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int, 
    post_data: PostUpdate, 
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user_id)
):
    """게시물 수정 (작성자만 가능)"""
    post_service = PostService(db)
    return post_service.update_post(post_id, post_data.dict(exclude_unset=True), current_user_id)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user_id)
):
    """게시물 삭제 (작성자만 가능)"""
    post_service = PostService(db)
    post_service.delete_post(post_id, current_user_id)
    return {}