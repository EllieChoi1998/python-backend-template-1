from contextlib import contextmanager
from utils.database import get_connection
from sqlalchemy.orm import Session
from typing import Optional

@contextmanager
def transaction_context(db: Optional[Session] = None):
    """
    트랜잭션 컨텍스트 매니저
    
    ORM 또는 직접 쿼리 모두에서 사용 가능한 트랜잭션 관리
    
    사용 예:
        with transaction_context(db) as tx:
            # 트랜잭션 내에서 작업 수행
            # 예외가 발생하면 자동으로 롤백
    """
    if db:  # ORM 세션 사용
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
    else:  # 직접 연결 사용
        conn = None
        try:
            conn = get_connection()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()