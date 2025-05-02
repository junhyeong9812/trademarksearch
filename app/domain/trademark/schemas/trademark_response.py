"""
상표 검색 결과 응답 모델

이 모듈은 상표 검색 API 응답을 위한 스키마를 정의합니다.
"""
from typing import List
from pydantic import BaseModel, Field
from app.domain.trademark.models.trademark_base import TrademarkBase

class TrademarkResponse(BaseModel):
    """상표 검색 결과 응답 모델"""
    total: int = Field(..., description="총 검색 결과 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지당 결과 수")
    results: List[TrademarkBase] = Field(..., description="상표 검색 결과 목록")