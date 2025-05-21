from repository.user import UserRepository
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db
from passlib.context import CryptContext
from typing import Optional, List, Dict, Any

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session = None):
        self.db = db
        self.user_repository = UserRepository
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """모든 사용자 조회"""
        return self.user_repository.get_all_users(self.db)
    
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """ID로 사용자 조회"""
        user = self.user_repository.get_user_by_id(user_id, self.db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """사용자명으로 사용자 조회"""
        return self.user_repository.get_user_by_username(username, self.db)
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 생성"""
        # 사용자명 중복 확인
        existing_user = self.get_user_by_username(user_data["username"])
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # 비밀번호 해싱
        user_data["password"] = self.get_password_hash(user_data["password"])
        
        return self.user_repository.create_user(user_data, self.db)
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 정보 수정"""
        # 사용자 존재 확인
        self.get_user_by_id(user_id)
        
        # 비밀번호가 포함된 경우 해싱
        if "password" in user_data:
            user_data["password"] = self.get_password_hash(user_data["password"])
        
        return self.user_repository.update_user(user_id, user_data, self.db)
    
    def delete_user(self, user_id: int) -> bool:
        """사용자 삭제"""
        # 사용자 존재 확인
        self.get_user_by_id(user_id)
        
        return self.user_repository.delete_user(user_id, self.db)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """사용자 인증"""
        user = self.get_user_by_username(username)
        
        if not user:
            return None
        
        if not self.verify_password(password, user["password"]):
            return None
        
        # 비밀번호 필드 제거
        if "password" in user:
            del user["password"]
        
        return user