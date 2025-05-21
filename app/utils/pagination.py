from typing import Generic, TypeVar, List, Dict, Any, Optional
from pydantic import BaseModel
from pydantic.generics import GenericModel
from fastapi import Query
from math import ceil

T = TypeVar('T')

class PageParams:
    """페이지네이션 파라미터"""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="페이지 번호"),
        page_size: int = Query(10, ge=1, le=100, description="페이지 크기")
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

class PageMetadata(BaseModel):
    """페이지네이션 메타데이터"""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool

class Page(GenericModel, Generic[T]):
    """페이지네이션된 결과를 위한 응답 모델"""
    items: List[T]
    metadata: PageMetadata

def paginate(
    items: List[Any],
    total_count: int,
    page_params: PageParams
) -> Dict[str, Any]:
    """항목 리스트를 페이지네이션된 결과로 변환"""
    total_pages = ceil(total_count / page_params.page_size)
    
    metadata = PageMetadata(
        page=page_params.page,
        page_size=page_params.page_size,
        total_items=total_count,
        total_pages=total_pages,
        has_next=page_params.page < total_pages,
        has_prev=page_params.page > 1
    )
    
    return {
        "items": items,
        "metadata": metadata
    }