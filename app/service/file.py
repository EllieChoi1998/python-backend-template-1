import os
import uuid
from fastapi import UploadFile, HTTPException
from typing import Dict, Any, List
import aiofiles
from sqlalchemy.orm import Session
from models import File
from sqlalchemy import text
from config import settings

class FileService:
    def __init__(self, db: Session = None):
        self.db = db
        self.upload_dir = settings.UPLOAD_DIR
        
        # 업로드 디렉토리가 없으면 생성
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    async def save_file(self, file: UploadFile, post_id: int) -> Dict[str, Any]:
        """파일 저장 및 DB에 기록"""
        # 파일명 생성 (중복 방지를 위한 UUID)
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # 파일 크기 계산
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # 파일 포인터 리셋
        
        # 파일 저장
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # DB에 파일 정보 저장
        if self.db:  # ORM 사용
            db_file = File(
                post_id=post_id,
                file_name=file.filename,
                file_path=file_path,
                file_size=file_size
            )
            self.db.add(db_file)
            self.db.commit()
            self.db.refresh(db_file)
            return {
                "id": db_file.id,
                "post_id": db_file.post_id,
                "file_name": db_file.file_name,
                "file_path": db_file.file_path,
                "file_size": db_file.file_size,
                "created_at": db_file.created_at
            }
        else:  # 직접 쿼리 사용
            from utils.database import execute_query
            query = """
            INSERT INTO files (post_id, file_name, file_path, file_size, created_at)
            VALUES (:post_id, :file_name, :file_path, :file_size, CURRENT_TIMESTAMP)
            RETURNING id, post_id, file_name, file_path, file_size, created_at
            """
            params = {
                "post_id": post_id,
                "file_name": file.filename,
                "file_path": file_path,
                "file_size": file_size
            }
            result = execute_query(query, params)
            return result[0] if result else None
    
    def get_files_by_post_id(self, post_id: int) -> List[Dict[str, Any]]:
        """게시물에 첨부된 파일 목록 조회"""
        if self.db:  # ORM 사용
            files = self.db.query(File).filter(
                File.post_id == post_id,
                File.deleted_at.is_(None)
            ).all()
            return [
                {
                    "id": file.id,
                    "post_id": file.post_id,
                    "file_name": file.file_name,
                    "file_path": file.file_path,
                    "file_size": file.file_size,
                    "created_at": file.created_at
                } for file in files
            ]
        else:  # 직접 쿼리 사용
            from utils.database import execute_query
            query = """
            SELECT id, post_id, file_name, file_path, file_size, created_at
            FROM files
            WHERE post_id = :post_id AND deleted_at IS NULL
            """
            return execute_query(query, {"post_id": post_id})
    
    def get_file_by_id(self, file_id: int) -> Dict[str, Any]:
        """ID로 파일 정보 조회"""
        if self.db:  # ORM 사용
            file = self.db.query(File).filter(
                File.id == file_id,
                File.deleted_at.is_(None)
            ).first()
            if not file:
                raise HTTPException(status_code=404, detail="File not found")
            return {
                "id": file.id,
                "post_id": file.post_id,
                "file_name": file.file_name,
                "file_path": file.file_path,
                "file_size": file.file_size,
                "created_at": file.created_at
            }
        else:  # 직접 쿼리 사용
            from utils.database import execute_query
            query = """
            SELECT id, post_id, file_name, file_path, file_size, created_at
            FROM files
            WHERE id = :file_id AND deleted_at IS NULL
            """
            result = execute_query(query, {"file_id": file_id})
            if not result:
                raise HTTPException(status_code=404, detail="File not found")
            return result[0]
    
    def delete_file(self, file_id: int, user_id: int) -> bool:
        """파일 삭제 (소프트 딜리트 + 권한 체크)"""
        # 파일 정보 조회
        file_info = self.get_file_by_id(file_id)
        
        # 게시물 작성자 확인 (파일 소유권 확인)
        from service.post import PostService
        post_service = PostService(self.db)
        post = post_service.get_post_by_id(file_info["post_id"])
        
        if post["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this file")
        
        # 파일 삭제 처리 (소프트 딜리트)
        if self.db:  # ORM 사용
            self.db.query(File).filter(File.id == file_id).update({
                "deleted_at": text("CURRENT_TIMESTAMP")
            })
            self.db.commit()
            return True
        else:  # 직접 쿼리 사용
            from utils.database import execute_query
            query = """
            UPDATE files
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = :file_id AND deleted_at IS NULL
            """
            result = execute_query(query, {"file_id": file_id}, fetch=False)
            return result > 0