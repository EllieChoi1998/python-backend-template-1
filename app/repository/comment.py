from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import execute_query, get_connection
from models import Comment

class CommentRepository:
    @staticmethod
    def get_comments_by_post_id(post_id: int, db: Session = None):
        """게시물에 달린 댓글 조회"""
        if db:  # ORM 사용
            return db.query(Comment).filter(
                Comment.post_id == post_id,
                Comment.deleted_at.is_(None)
            ).order_by(Comment.created_at.asc()).all()
        else:  # 직접 쿼리 사용
            query = """
            SELECT c.id, c.post_id, c.user_id, c.content, c.created_at, c.modified_at,
                   u.username as author_name
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = :post_id 
            AND c.deleted_at IS NULL
            ORDER BY c.created_at ASC
            """
            return execute_query(query, {"post_id": post_id})
    
    @staticmethod
    def get_comment_by_id(comment_id: int, db: Session = None):
        """ID로 댓글 조회"""
        if db:  # ORM 사용
            return db.query(Comment).filter(
                Comment.id == comment_id,
                Comment.deleted_at.is_(None)
            ).first()
        else:  # 직접 쿼리 사용
            query = """
            SELECT c.id, c.post_id, c.user_id, c.content, c.created_at, c.modified_at,
                   u.username as author_name
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = :comment_id 
            AND c.deleted_at IS NULL
            """
            result = execute_query(query, {"comment_id": comment_id})
            return result[0] if result else None
    
    @staticmethod
    def create_comment(comment_data: dict, db: Session = None):
        """댓글 생성"""
        if db:  # ORM 사용
            comment = Comment(**comment_data)
            db.add(comment)
            db.commit()
            db.refresh(comment)
            return comment
        else:  # 직접 쿼리 사용
            query = """
            INSERT INTO comments (post_id, user_id, content, created_at, modified_at)
            VALUES (:post_id, :user_id, :content, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, post_id, user_id, content, created_at, modified_at
            """
            with get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(query, comment_data)
                    result = cursor.fetchone()
                    conn.commit()
                    
                    # 결과를 딕셔너리로 변환
                    columns = [col[0] for col in cursor.description]
                    comment = dict(zip(columns, result))
                    return comment
                except Exception as e:
                    conn.rollback()
                    raise e
                finally:
                    cursor.close()
    
    @staticmethod
    def update_comment(comment_id: int, comment_data: dict, db: Session = None):
        """댓글 수정"""
        if db:  # ORM 사용
            db.query(Comment).filter(Comment.id == comment_id).update({
                **comment_data,
                "modified_at": text("CURRENT_TIMESTAMP")
            })
            db.commit()
            return db.query(Comment).filter(Comment.id == comment_id).first()
        else:  # 직접 쿼리 사용
            query = """
            UPDATE comments
            SET content = :content, modified_at = CURRENT_TIMESTAMP
            WHERE id = :comment_id AND deleted_at IS NULL
            """
            params = {"content": comment_data["content"], "comment_id": comment_id}
            execute_query(query, params, fetch=False)
            
            # 업데이트된 댓글 정보 조회
            return CommentRepository.get_comment_by_id(comment_id)
    
    @staticmethod
    def delete_comment(comment_id: int, db: Session = None):
        """댓글 삭제 (soft delete)"""
        if db:  # ORM 사용
            db.query(Comment).filter(Comment.id == comment_id).update({
                "deleted_at": text("CURRENT_TIMESTAMP")
            })
            db.commit()
            return True
        else:  # 직접 쿼리 사용
            query = """
            UPDATE comments
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = :comment_id AND deleted_at IS NULL
            """
            result = execute_query(query, {"comment_id": comment_id}, fetch=False)
            return result > 0