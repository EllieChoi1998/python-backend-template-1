from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models import get_db
from service.file import FileService
from service.post import PostService
from auth.jwt_bearer import get_current_user_id
from typing import List
import os
from pydantic import BaseModel

router = APIRouter(prefix="/api/files", tags=["Files"])

# 응답 모델
class FileResponse(BaseModel):
    id: int
    post_id: int
    file_name: str
    file_size: int
    created_at: str

@router.post("/upload/{post_id}", response_model=FileResponse)
async def upload_file(
    post_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """게시물에 파일 업로드 (작성자만 가능)"""
    # 게시물 소유권 확인
    post_service = PostService(db)
    post = post_service.get_post_by_id(post_id)
    
    if post["user_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to upload files to this post")
    
    # 파일 저장
    file_service = FileService(db)
    file_info = await file_service.save_file(file, post_id)
    
    return file_info

@router.get("/post/{post_id}", response_model=List[FileResponse])
def get_files_by_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """게시물에 첨부된 파일 목록 조회"""
    file_service = FileService(db)
    return file_service.get_files_by_post_id(post_id)

@router.get("/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """파일 다운로드"""
    file_service = FileService(db)
    file_info = file_service.get_file_by_id(file_id)
    
    file_path = file_info["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=file_path,
        filename=file_info["file_name"],
        media_type="application/octet-stream"
    )

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """파일 삭제 (게시물 작성자만 가능)"""
    file_service = FileService(db)
    file_service.delete_file(file_id, current_user_id)
    return {}