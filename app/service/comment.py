from repository.comment import CommentRepository
from repository.post import PostRepository
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db
from typing import List, Dict, Any, Optional

class CommentService:
    def __init__(self, db: Session = None):
        self.db = db
        self.comment_repository = CommentRepository
        self.post_repository = PostRepository
    
    def get_comments_by_post_id(self, post_id: int) -> List[Dict[str, Any]]:
        """게시물에 달린 댓글 조회"""
        # 게시물 존재 확인
        post = self.post_repository.get_post_by_id(post_id, self.db)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return self.comment_repository.get_comments_by_post_id(post_id, self.db)
    
    def get_comment_by_id(self, comment_id: int) -> Dict[str, Any]:
        """ID로 댓글 조회"""
        comment = self.comment_repository.get_comment_by_id(comment_id, self.db)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment
    
    def create_comment(self, comment_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """댓글 생성"""
        # 게시물 존재 확인
        post_id = comment_data["post_id"]
        post = self.post_repository.get_post_by_id(post_id, self.db)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # 사용자 ID 설정
        comment_data["user_id"] = user_id
        
        return self.comment_repository.create_comment(comment_data, self.db)
    
    def update_comment(self, comment_id: int, comment_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """댓글 수정"""
        # 댓글 존재 확인
        comment = self.get_comment_by_id(comment_id)
        
        # 수정 권한 확인 (작성자인지)
        if comment["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this comment")
        
        return self.comment_repository.update_comment(comment_id, comment_data, self.db)
    
    def delete_comment(self, comment_id: int, user_id: int) -> bool:
        """댓글 삭제"""
        # 댓글 존재 확인
        comment = self.get_comment_by_id(comment_id)
        
        # 삭제 권한 확인 (작성자인지)
        if comment["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
        return self.comment_repository.delete_comment(comment_id, self.db)