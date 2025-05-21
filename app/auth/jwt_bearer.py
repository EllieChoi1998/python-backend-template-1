from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.jwt_handler import verify_token
from service.user import UserService
from models import get_db
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme")
            
            payload = self.verify_token(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=403, detail="Invalid token or expired token")
            
            # 사용자 확인
            user_service = UserService(db)
            user = user_service.get_user_by_id(payload["id"])
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return payload
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        return verify_token(token)

# 현재 로그인한 사용자의 ID 가져오기
def get_current_user_id(token_data: Dict[str, Any] = Depends(JWTBearer())) -> int:
    return token_data["id"]