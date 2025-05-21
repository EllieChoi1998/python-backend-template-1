from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config import settings
from typing import Generator

# Oracle 데이터베이스 연결 URL
DATABASE_URL = f"oracle+oracledb://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_SERVICE}"

# 데이터베이스 엔진 생성
engine = create_engine(
    DATABASE_URL, 
    pool_size=5, 
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # 30분마다 연결 갱신
    echo=settings.DEBUG  # SQL 로깅
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델의 기본 클래스 생성
Base = declarative_base()

# 사용자 테이블 모델
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(60), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    # 관계 정의
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

# 게시물 테이블 모델
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    # 관계 정의
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

# 댓글 테이블 모델
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    # 관계 정의
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

# 파일 테이블 모델
class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    file_name = Column(String(260), nullable=False)
    file_path = Column(String(260), nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)

# 데이터베이스 테이블 생성 함수
def create_tables():
    Base.metadata.create_all(bind=engine)

# 데이터베이스 세션 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()