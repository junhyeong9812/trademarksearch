"""
상표 상세 조회 응답 모델

이 모듈은 상표 상세 조회 API 응답을 위한 스키마를 정의합니다.
"""
from pydantic import BaseModel, Field
from app.domain.trademark.models.trademark_base import TrademarkBase

class TrademarkDetailResponse(BaseModel):
    """상표 상세 조회 응답 모델"""
    data: TrademarkBase = Field(..., description="상표 상세 정보")