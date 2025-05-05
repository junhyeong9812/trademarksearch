"""
상표 검색 매개변수 모델

이 모듈은 상표 검색 API 요청 매개변수를 위한 스키마를 정의합니다.
"""
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import date
from app.core.config import settings

class SortOrder(str, Enum):
    """정렬 방향 열거형"""
    ASC = "asc"
    DESC = "desc"

class SortField(str, Enum):
    """정렬 필드 열거형"""
    APPLICATION_DATE = "applicationDate"
    REGISTRATION_DATE = "registrationDate"
    PRODUCT_NAME = "productName"
    PRODUCT_NAME_ENG = "productNameEng"
    VIEW_COUNT = "viewCount"
    PID = "pid"

class SortOption(BaseModel):
    """정렬 옵션 모델"""
    field: SortField
    order: SortOrder = SortOrder.DESC

class TrademarkSearchParams(BaseModel):
    """상표 검색 매개변수 모델"""
    query: Optional[str] = Field(None, description="검색어 (상표명)")
    status: Optional[str] = Field(None, description="상표 등록 상태 (등록, 출원, 거절 등)")
    main_code: Optional[str] = Field(None, description="상품 주 분류 코드")
    sub_code: Optional[str] = Field(None, description="상품 유사군 코드")
    start_date: Optional[date] = Field(None, description="검색 시작일 (출원일 기준)")
    end_date: Optional[date] = Field(None, description="검색 종료일 (출원일 기준)")
    page: int = Field(1, description="페이지 번호", ge=1)
    size: int = Field(settings.DEFAULT_PAGE_SIZE, description="페이지당 결과 수", ge=1, le=settings.MAX_PAGE_SIZE)
    sort: Optional[List[SortOption]] = Field(None, description="정렬 옵션 목록")