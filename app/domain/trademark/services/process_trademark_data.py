"""
상표 데이터 전처리 함수

이 모듈은 상표 데이터를 Elasticsearch에 색인하기 전에 전처리하는 함수를 제공합니다.
"""
import logging
from typing import Dict, Any
from app.domain.trademark.services.helpers import format_date, process_list_field

logger = logging.getLogger(__name__)

def process_trademark_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """상표 데이터 전처리 (날짜 형식 변환, 리스트 필드 처리 등)"""
    processed_data = {}
    
    # 기본 필드 복사
    for key, value in data.items():
        if value == "null" or value is None:
            processed_data[key] = None
        else:
            processed_data[key] = value
    
    # 날짜 필드 처리
    date_fields = ["applicationDate", "publicationDate", "registrationDate", 
                  "internationalRegDate", "priorityClaimDateList"]
    
    for field in date_fields:
        if field in data and data[field]:
            # 리스트 형태의 날짜 필드 처리
            if isinstance(data[field], list):
                processed_data[field] = [format_date(d) for d in data[field] if d and d != "null"]
            else:
                processed_data[field] = format_date(data[field])
    
    # 리스트 필드 처리
    list_fields = ["registrationNumber", "internationalRegNumbers", 
                  "priorityClaimNumList", "asignProductMainCodeList",
                  "asignProductSubCodeList", "viennaCodeList"]
    
    for field in list_fields:
        if field in data:
            processed_data[field] = process_list_field(data[field])
    
    return processed_data