from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import JWTError
import logging
from typing import Any, Dict, Optional

# 로깅 설정
logger = logging.getLogger(__name__)

def setup_error_handlers(app: FastAPI) -> None:
    """애플리케이션에 에러 핸들러 설정"""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """요청 검증 오류 핸들러"""
        errors = []
        for error in exc.errors():
            error_location = " -> ".join([str(loc) for loc in error["loc"]])
            errors.append({
                "location": error_location,
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(f"Validation error: {errors}")
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Invalid request",
                "errors": errors
            }
        )
    
    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError) -> JSONResponse:
        """JWT 관련 오류 핸들러"""
        logger.warning(f"JWT error: {str(exc)}")
        
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Invalid authentication credentials"
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        """데이터베이스 무결성 제약 오류 핸들러"""
        error_message = str(exc)
        logger.error(f"Database integrity error: {error_message}")
        
        # 중복 키 오류 처리
        if "ORA-00001" in error_message:  # 고유 제약 조건 위반
            constraint_name = error_message.split("ORA-00001")[1].split("(")[0].strip()
            return JSONResponse(
                status_code=409,
                content={
                    "detail": f"Resource already exists",
                    "constraint": constraint_name
                }
            )
        
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Database integrity error"
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """SQLAlchemy 오류 핸들러"""
        logger.error(f"Database error: {str(exc)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database error occurred"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """일반 예외 핸들러"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error"
            }
        )