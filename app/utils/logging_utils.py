import logging
import time
import json
from typing import Dict, Any, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# 로깅 설정
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    요청 및 응답에 대한 로깅을 수행하는 미들웨어
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 요청 정보 로깅
        request_id = request.headers.get("X-Request-ID", "-")
        client_ip = request.client.host if request.client else "-"
        request_path = request.url.path
        request_method = request.method
        
        # 요청 로그
        logger.info(
            f"Started {request_method} {request_path} for {client_ip} [Request ID: {request_id}]"
        )
        
        # 응답 처리
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 응답 로그
            logger.info(
                f"Completed {response.status_code} {request_method} {request_path} "
                f"in {process_time:.3f}s [Request ID: {request_id}]"
            )
            
            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error during {request_method} {request_path}: {str(e)} "
                f"in {process_time:.3f}s [Request ID: {request_id}]"
            )
            raise

def log_request_info(request_data: Dict[str, Any], user_id: int = None) -> None:
    """
    요청 데이터를 로깅하는 유틸리티 함수
    """
    masked_data = mask_sensitive_data(request_data)
    logger.info(
        f"Request data from user {user_id or 'anonymous'}: {json.dumps(masked_data)}"
    )

def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    민감한 데이터를 마스킹하는 함수
    """
    sensitive_fields = ["password", "token", "secret", "credit_card", "ssn"]
    
    # 딕셔너리를 복사하여 원본을 변경하지 않음
    masked_data = dict(data)
    
    for key in masked_data:
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            if isinstance(masked_data[key], str) and masked_data[key]:
                masked_data[key] = "********"
    
    return masked_data