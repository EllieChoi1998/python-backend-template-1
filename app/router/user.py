from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import get_db
from service.user import UserService
from auth.jwt_handler import create_access_token
from auth.jwt_bearer import JWTBearer, get_current_user_id
from typing import List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/api/users", tags=["Users"])

# 요청 및 응답 모델
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|user)$")

class UserUpdate(BaseModel):
    username: str = Field(None, min_length=3, max_length=20)
    password: str = Field(None, min_length=6)
    email: EmailStr = None
    role: str = Field(None, pattern="^(admin|user)$")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 라우트 정의
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """새 사용자 등록"""
    user_service = UserService(db)
    new_user = user_service.create_user(user.dict())
    return new_user

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """사용자 로그인"""
    user_service = UserService(db)
    user = user_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"id": user["id"], "username": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), _: Dict[str, Any] = Depends(JWTBearer())):
    """모든 사용자 조회 (인증 필요)"""
    user_service = UserService(db)
    return user_service.get_all_users()

@router.get("/me", response_model=UserResponse)
def get_current_user(
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user_id)
):
    """현재 로그인한 사용자 정보 조회"""
    user_service = UserService(db)
    return user_service.get_user_by_id(current_user_id)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    _: Dict[str, Any] = Depends(JWTBearer())
):
    """특정 사용자 조회 (인증 필요)"""
    user_service = UserService(db)
    return user_service.get_user_by_id(user_id)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user_id)
):
    """사용자 정보 수정 (자신의 정보만 수정 가능)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    user_service = UserService(db)
    return user_service.update_user(user_id, user_data.dict(exclude_unset=True))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user_id)
):
    """사용자 삭제 (자신의 계정만 삭제 가능)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    
    user_service = UserService(db)
    user_service.delete_user(user_id)
    return {}