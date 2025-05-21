from models import Base, engine, create_tables
import os
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """테이블 생성 스크립트 실행"""
    try:
        load_dotenv()  # 환경 변수 로드
        logger.info("Starting database table creation...")
        
        # 테이블 생성
        create_tables()
        
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

if __name__ == "__main__":
    main()