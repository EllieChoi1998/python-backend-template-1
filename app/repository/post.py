from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import execute_query, get_connection
from models import Post

class PostRepository:
    @staticmethod
    def get_all_posts(limit: int = 100, offset: int = 0, db: Session = None):
        """모든 게시물 조회"""
        if db:  # ORM 사용
            return db.query(Post).filter(Post.deleted_at.is_(None)) \
                .order_by(Post.created_at.desc()) \
                .limit(limit).offset(offset).all()
        else:  # 직접 쿼리 사용
            query = """
            SELECT p.id, p.user_id, p.title, p.content, p.view_count, 
                   p.created_at, p.modified_at, u.username as author_name
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.deleted_at IS NULL
            ORDER BY p.created_at DESC
            OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
            """
            return execute_query(query, {"limit": limit, "offset": offset})
    
    @staticmethod
    def get_post_by_id(post_id: int, db: Session = None):
        """ID로 게시물 조회"""
        if db:  # ORM 사용
            return db.query(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)).first()
        else:  # 직접 쿼리 사용
            query = """
            SELECT p.id, p.user_id, p.title, p.content, p.view_count, 
                   p.created_at, p.modified_at, u.username as author_name
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = :post_id AND p.deleted_at IS NULL
            """
            result = execute_query(query, {"post_id": post_id})
            return result[0] if result else None
    
    @staticmethod
    def create_post(post_data: dict, db: Session = None):
        """게시물 생성"""
        if db:  # ORM 사용
            post = Post(**post_data)
            db.add(post)
            db.commit()
            db.refresh(post)
            return post
        else:  # 직접 쿼리 사용
            query = """
            INSERT INTO posts (user_id, title, content, view_count, created_at, modified_at)
            VALUES (:user_id, :title, :content, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, user_id, title, content, view_count, created_at, modified_at
            """
            with get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(query, post_data)
                    result = cursor.fetchone()
                    conn.commit()
                    
                    # 결과를 딕셔너리로 변환
                    columns = [col[0] for col in cursor.description]
                    post = dict(zip(columns, result))
                    return post
                except Exception as e:
                    conn.rollback()
                    raise e
                finally:
                    cursor.close()
    
    @staticmethod
    def update_post(post_id: int, post_data: dict, db: Session = None):
        """게시물 수정"""
        if db:  # ORM 사용
            db.query(Post).filter(Post.id == post_id).update({
                **post_data,
                "modified_at": text("CURRENT_TIMESTAMP")
            })
            db.commit()
            return db.query(Post).filter(Post.id == post_id).first()
        else:  # 직접 쿼리 사용
            set_clause = ", ".join([f"{key} = :{key}" for key in post_data.keys()])
            query = f"""
            UPDATE posts
            SET {set_clause}, modified_at = CURRENT_TIMESTAMP
            WHERE id = :post_id AND deleted_at IS NULL
            """
            params = {**post_data, "post_id": post_id}
            execute_query(query, params, fetch=False)
            
            # 업데이트된 게시물 정보 조회
            return PostRepository.get_post_by_id(post_id)
    
    @staticmethod
    def delete_post(post_id: int, db: Session = None):
        """게시물 삭제 (soft delete)"""
        if db:  # ORM 사용
            db.query(Post).filter(Post.id == post_id).update({
                "deleted_at": text("CURRENT_TIMESTAMP")
            })
            db.commit()
            return True
        else:  # 직접 쿼리 사용
            query = """
            UPDATE posts
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = :post_id AND deleted_at IS NULL
            """
            result = execute_query(query, {"post_id": post_id}, fetch=False)
            return result > 0
    
    @staticmethod
    def increment_view_count(post_id: int, db: Session = None):
        """조회수 증가"""
        if db:  # ORM 사용
            post = db.query(Post).filter(Post.id == post_id).first()
            if post:
                post.view_count += 1
                db.commit()
            return post
        else:  # 직접 쿼리 사용
            query = """
            UPDATE posts
            SET view_count = view_count + 1
            WHERE id = :post_id AND deleted_at IS NULL
            """
            return execute_query(query, {"post_id": post_id}, fetch=False)