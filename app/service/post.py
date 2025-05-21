from repository.post import PostRepository
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db
from typing import List, Dict, Any, Optional

class PostService:
    def __init__(self, db: Session = None):
        self.db = db
        self.post_repository = PostRepository
    
    def get_all_posts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """모든 게시물 조회"""
        return self.post_repository.get_all_posts(limit, offset, self.db)
    
    def get_post_by_id(self, post_id: int, increment_views: bool = False) -> Dict[str, Any]:
        """ID로 게시물 조회"""
        post = self.post_repository.get_post_by_id(post_id, self.db)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # 조회수 증가
        if increment_views:
            self.post_repository.increment_view_count(post_id, self.db)
            post["view_count"] = post.get("view_count", 0) + 1
        
        return post
    
    def create_post(self, post_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """게시물 생성"""
        post_data["user_id"] = user_id
        return self.post_repository.create_post(post_data, self.db)
    
    def update_post(self, post_id: int, post_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """게시물 수정"""
        # 게시물 존재 확인
        post = self.get_post_by_id(post_id)
        
        # 수정 권한 확인 (작성자인지)
        if post["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this post")
        
        return self.post_repository.update_post(post_id, post_data, self.db)
    
    def delete_post(self, post_id: int, user_id: int) -> bool:
        """게시물 삭제"""
        # 게시물 존재 확인
        post = self.get_post_by_id(post_id)
        
        # 삭제 권한 확인 (작성자인지)
        if post["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
        return self.post_repository.delete_post(post_id, self.db)