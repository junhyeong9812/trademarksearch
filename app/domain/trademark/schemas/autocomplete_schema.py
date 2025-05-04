"""
자동완성 관련 스키마

이 모듈은 자동완성 API 요청/응답 모델을 정의합니다.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class AutocompleteSuggestion(BaseModel):
    """자동완성 제안 항목"""
    text: str = Field(..., description="제안된 상표명")
    productNameEng: Optional[str] = Field(None, description="영문 상표명")
    score: float = Field(..., description="매칭 스코어")
    highlight: Optional[Dict[str, List[str]]] = Field(None, description="하이라이트된 부분")

class AutocompleteRequest(BaseModel):
    """자동완성 요청 모델"""
    query: str = Field(..., description="검색어", min_length=1)
    size: int = Field(10, description="반환할 제안 수", ge=1, le=20)

class AutocompleteResponse(BaseModel):
    """자동완성 응답 모델"""
    suggestions: List[AutocompleteSuggestion] = Field(..., description="자동완성 제안 목록")
    total: int = Field(..., description="총 제안 수")