from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.database import init_db
from router import user_router, post_router, comment_router, file_router
import os
import logging
from contextlib import asynccontextmanager
from config import settings
from utils.error_handlers import setup_error_handlers

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 시작 및 종료 이벤트 핸들러
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행
    logger.info("Application startup")
    init_db()  # 데이터베이스 풀 초기화
    
    yield  # 애플리케이션 실행 중
    
    # 애플리케이션 종료 시 실행
    logger.info("Application shutdown")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI application with Oracle DB using Repository-Service-Router pattern",
    version="1.0.0",
    lifespan=lifespan,
)

# 에러 핸들러 설정
setup_error_handlers(app)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(user_router.router)
app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(file_router.router)

# 정적 파일 마운트 (업로드된 파일을 직접 제공하려는 경우)
# 주의: 프로덕션에서는 보안을 위해 Nginx 등을 사용하는 것이 좋음.
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} - FastAPI with Oracle DB",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """애플리케이션 상태 확인"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    
    host = settings.HOST if hasattr(settings, "HOST") else "0.0.0.0"
    port = settings.PORT if hasattr(settings, "PORT") else 8000
    reload = settings.DEBUG
    
    logger.info(f"Starting server on {host}:{port} (reload={reload})")
    uvicorn.run("main:app", host=host, port=port, reload=reload)