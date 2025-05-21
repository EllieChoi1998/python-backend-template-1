from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import execute_query, get_connection
from models import User

class UserRepository:
    @staticmethod
    def get_all_users(db: Session = None):
        """모든 사용자 조회"""
        if db:  # ORM 사용
            return db.query(User).filter(User.deleted_at.is_(None)).all()
        else:  # 직접 쿼리 사용
            query = """
            SELECT id, username, email, role, created_at, modified_at
            FROM users
            WHERE deleted_at IS NULL
            """
            return execute_query(query)
    
    @staticmethod
    def get_user_by_id(user_id: int, db: Session = None):
        """ID로 사용자 조회"""
        if db:  # ORM 사용
            return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        else:  # 직접 쿼리 사용
            query = """
            SELECT id, username, email, role, created_at, modified_at
            FROM users
            WHERE id = :user_id AND deleted_at IS NULL
            """
            result = execute_query(query, {"user_id": user_id})
            return result[0] if result else None
    
    @staticmethod
    def get_user_by_username(username: str, db: Session = None):
        """사용자명으로 사용자 조회"""
        if db:  # ORM 사용
            return db.query(User).filter(User.username == username, User.deleted_at.is_(None)).first()
        else:  # 직접 쿼리 사용
            query = """
            SELECT id, username, email, role, created_at, modified_at, password
            FROM users
            WHERE username = :username AND deleted_at IS NULL
            """
            result = execute_query(query, {"username": username})
            return result[0] if result else None
    
    @staticmethod
    def create_user(user_data: dict, db: Session = None):
        """사용자 생성"""
        if db:  # ORM 사용
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        else:  # 직접 쿼리 사용
            query = """
            INSERT INTO users (username, password, email, role, created_at, modified_at)
            VALUES (:username, :password, :email, :role, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, username, email, role, created_at, modified_at
            """
            with get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(query, user_data)
                    result = cursor.fetchone()
                    conn.commit()
                    
                    # 결과를 딕셔너리로 변환
                    columns = [col[0] for col in cursor.description]
                    user = dict(zip(columns, result))
                    return user
                except Exception as e:
                    conn.rollback()
                    raise e
                finally:
                    cursor.close()
    
    @staticmethod
    def update_user(user_id: int, user_data: dict, db: Session = None):
        """사용자 정보 수정"""
        if db:  # ORM 사용
            db.query(User).filter(User.id == user_id).update({
                **user_data,
                "modified_at": text("CURRENT_TIMESTAMP")
            })
            db.commit()
            return db.query(User).filter(User.id == user_id).first()
        else:  # 직접 쿼리 사용
            set_clause = ", ".join([f"{key} = :{key}" for key in user_data.keys()])
            query = f"""
            UPDATE users
            SET {set_clause}, modified_at = CURRENT_TIMESTAMP
            WHERE id = :user_id AND deleted_at IS NULL
            """
            params = {**user_data, "user_id": user_id}
            execute_query(query, params, fetch=False)
            
            # 업데이트된 사용자 정보 조회
            return UserRepository.get_user_by_id(user_id)
    
    @staticmethod
    def delete_user(user_id: int, db: Session = None):
        """사용자 삭제 (soft delete)"""
        if db:  # ORM 사용
            db.query(User).filter(User.id == user_id).update({
                "deleted_at": text("CURRENT_TIMESTAMP")
            })
            db.commit()
            return True
        else:  # 직접 쿼리 사용
            query = """
            UPDATE users
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = :user_id AND deleted_at IS NULL
            """
            result = execute_query(query, {"user_id": user_id}, fetch=False)
            return result > 0