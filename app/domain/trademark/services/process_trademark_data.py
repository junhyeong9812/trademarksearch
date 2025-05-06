"""
상표 데이터 전처리 함수

이 모듈은 상표 데이터를 Elasticsearch에 색인하기 전에 전처리하는 함수를 제공합니다.
초성 추출 및 영문 상표명 발음 변환 기능이 포함되어 있습니다.
"""
from loguru import logger
from typing import Dict, Any, Optional

from app.domain.trademark.services.helpers import format_date, process_list_field
from app.domain.trademark.services.chosung_utils import extract_chosung
from app.domain.trademark.services.pronunciation_utils import english_to_korean_pronunciation
from app.domain.trademark.services.pid_utils import generate_next_pid

def process_trademark_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    상표 데이터 전처리 (날짜 형식 변환, 리스트 필드 처리, 초성 추출, 발음 변환 등)
    
    Args:
        data (Dict[str, Any]): 원본 상표 데이터
        
    Returns:
        Dict[str, Any]: 전처리된 상표 데이터
    """
    processed_data = {}
    
    # 고유 ID 생성 (pid)
    if 'pid' not in data or not data['pid']:
        processed_data['pid'] = generate_next_pid()
    else:
        processed_data['pid'] = data['pid']
    
    # 조회수 초기화
    if 'viewCount' not in data or data['viewCount'] is None:
        processed_data['viewCount'] = 0
    else:
        processed_data['viewCount'] = data['viewCount']
    
    # 기본 필드 복사
    for key, value in data.items():
        if key not in processed_data:  # pid와 viewCount는 이미 처리했으므로 건너뜀
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
    
    # 초성 추출 처리
    if 'productName' in data and data['productName']:
        try:
            chosung = extract_chosung(data['productName'])
            if chosung:
                processed_data['productName_chosung'] = chosung
                logger.debug(f"상표명 '{data['productName']}'의 초성: {chosung}")
        except Exception as e:
            logger.error(f"초성 추출 중 오류 발생 - 상표명: {data['productName']}, 오류: {str(e)}", exc_info=True)
    
    # 영문 상표명의 한글 발음 변환
    if 'productNameEng' in data and data['productNameEng']:
        try:
            eng_pronunciation = english_to_korean_pronunciation(data['productNameEng'])
            if eng_pronunciation:
                processed_data['productNameEngPronunciation'] = eng_pronunciation
                logger.debug(f"영문 상표명 '{data['productNameEng']}'의 한글 발음: {eng_pronunciation}")
                
                # 발음의 초성도 추출하여 저장
                chosung = extract_chosung(eng_pronunciation)
                if chosung:
                    processed_data['productNameEngPronunciation_chosung'] = chosung
                    logger.debug(f"영문 상표명 발음 '{eng_pronunciation}'의 초성: {chosung}")
        except Exception as e:
            logger.error(f"발음 변환 중 오류 발생 - 영문 상표명: {data['productNameEng']}, 오류: {str(e)}", exc_info=True)
    
    return processed_data