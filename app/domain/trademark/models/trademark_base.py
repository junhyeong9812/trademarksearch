"""
상표 데이터 기본 모델

이 모듈은 상표 데이터의 기본 엔티티 모델을 정의합니다.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class TrademarkBase(BaseModel):
    """상표 데이터 기본 모델"""
    pid: Optional[str] = None
    productName: Optional[str] = None
    productNameEng: Optional[str] = None
    productName_chosung: Optional[str] = None  # 상표명 초성
    productNameEngPronunciation: Optional[str] = None  # 영문 상표명의 한글 발음
    productNameEngPronunciation_chosung: Optional[str] = None  # 영문 상표명 한글 발음의 초성
    applicationNumber: Optional[str] = None
    applicationDate: Optional[date] = None
    registerStatus: Optional[str] = None
    publicationNumber: Optional[str] = None
    publicationDate: Optional[date] = None
    registrationNumber: Optional[List[str]] = None
    registrationDate: Optional[List[date]] = None
    internationalRegNumbers: Optional[List[str]] = None
    internationalRegDate: Optional[List[date]] = None
    priorityClaimNumList: Optional[List[str]] = None
    priorityClaimDateList: Optional[List[date]] = None
    asignProductMainCodeList: Optional[List[str]] = None
    asignProductSubCodeList: Optional[List[str]] = None
    viennaCodeList: Optional[List[str]] = None
    viewCount: int = Field(default=0, description="상표 조회수")