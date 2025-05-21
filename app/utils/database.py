import oracledb
from contextlib import contextmanager
from config import settings

# 데이터베이스 연결 풀 생성
pool = None

def init_db():
    """애플리케이션 시작 시 연결 풀 초기화"""
    global pool
    try:
        pool = oracledb.create_pool(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dsn=f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_SERVICE}",
            min=2,  # 최소 연결 수
            max=10,  # 최대 연결 수
            increment=1,  # 증가 단계
            getmode=oracledb.POOL_GETMODE_WAIT
        )
        print("Database pool created successfully")
    except Exception as e:
        print(f"Error creating database pool: {e}")
        raise

@contextmanager
def get_connection():
    """데이터베이스 연결을 제공하는 컨텍스트 매니저"""
    connection = None
    try:
        if pool is None:
            init_db()
        connection = pool.acquire()
        yield connection
    except Exception as e:
        print(f"Database connection error: {e}")
        raise
    finally:
        if connection:
            pool.release(connection)

def execute_query(query, params=None, fetch=True):
    """쿼리 실행 헬퍼 함수"""
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params or {})
            if fetch:
                result = cursor.fetchall()
                # 컬럼 이름 가져오기
                columns = [col[0] for col in cursor.description]
                # 결과를 딕셔너리 리스트로 변환
                return [dict(zip(columns, row)) for row in result]
            else:
                connection.commit()
                return cursor.rowcount
        except Exception as e:
            connection.rollback()
            print(f"Query execution error: {e}")
            raise
        finally:
            cursor.close()