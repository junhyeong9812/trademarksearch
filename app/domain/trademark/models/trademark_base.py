"""
상표 데이터 기본 모델

이 모듈은 상표 데이터의 기본 엔티티 모델을 정의합니다.
"""
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class TrademarkBase(BaseModel):
    """상표 데이터 기본 모델"""
    productName: Optional[str] = None
    productNameEng: Optional[str] = None
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