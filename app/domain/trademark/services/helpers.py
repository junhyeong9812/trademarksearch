"""
상표 데이터 처리를 위한 유틸리티 함수들

이 모듈은 데이터 처리에 필요한 헬퍼 함수들을 제공합니다.
"""
import logging
from typing import List, Any, Optional

logger = logging.getLogger(__name__)

def format_date(date_str: str) -> Optional[str]:
    """YYYYMMDD 형식의 날짜 문자열을 ISO 형식으로 변환"""
    if not date_str or date_str == "null":
        return None
    try:
        # YYYYMMDD 형식을 YYYY-MM-DD 형식으로 변환
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    except Exception:
        logger.warning(f"날짜 변환 실패: {date_str}")
        return None

def process_list_field(field_value: Any) -> List:
    """리스트 필드 처리 (None 또는 null 문자열이면 빈 리스트 반환)"""
    if field_value is None or field_value == "null":
        return None
    if isinstance(field_value, list):
        return field_value
    return [field_value]  # 단일 값인 경우 리스트로 변환