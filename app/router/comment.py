from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import get_db
from service.comment import CommentService
from auth.jwt_bearer import get_current_user_id
from typing import List, Dict, Any
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/comments", tags=["Comments"])

# 요청 및 응답 모델
class CommentCreate(BaseModel):
    post_id: int
    content: str = Field(..., min_length=1)

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)

class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: str
    modified_at: str
    author_name: str = None

# 라우트 정의
@router.get("/post/{post_id}", response_model=List[CommentResponse])
def get_comments_by_post(post_id: int, db: Session = Depends(get_db)):
    """게시물에 달린 댓글 조회"""
    comment_service = CommentService(db)
    return comment_service.get_comments_by_post_id(post_id)

@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """특정 댓글 조회"""
    comment_service = CommentService(db)
    return comment_service.get_comment_by_id(comment_id)

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: CommentCreate, 
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user_id)
):
    """새 댓글 작성 (인증 필요)"""
    comment_service = CommentService(db)
    return comment_service.create_comment(comment.dict(), current_user_id)

@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """댓글 수정 (작성자만 가능)"""
    comment_service = CommentService(db)
    return comment_service.update_comment(comment_id, comment_data.dict(), current_user_id)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """댓글 삭제 (작성자만 가능)"""
    comment_service = CommentService(db)
    comment_service.delete_comment(comment_id, current_user_id)
    return {}