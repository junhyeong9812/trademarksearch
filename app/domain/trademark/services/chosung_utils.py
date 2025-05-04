"""
초성 관련 유틸리티 함수

이 모듈은 한글 텍스트에서 초성을 추출하고 검색어가 초성인지 확인하는 유틸리티 함수를 제공합니다.
"""
from loguru import logger
from typing import Optional

# 한글 초성 리스트
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
# 초성 문자 집합 (검색용)
CHOSUNG_SET = set('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')

def extract_chosung(text: str) -> Optional[str]:
    """
    한글 문자열에서 초성만 추출하여 반환
    
    Args:
        text (str): 초성을 추출할 텍스트
        
    Returns:
        Optional[str]: 추출된 초성 문자열, 입력이 None이면 None 반환
    """
    if text is None:
        return None
        
    # 빈 문자열은 빈 문자열 반환 (None이 아님)
    if text == "":
        return ""
    
    result = []
    
    try:
        for char in text:
            if '가' <= char <= '힣':  # 한글 문자인 경우
                # 한글 유니코드 값에서 초성 인덱스 계산
                char_code = ord(char) - ord('가')
                chosung_index = char_code // 588
                result.append(CHOSUNG_LIST[chosung_index])
            else:
                # 한글이 아닌 문자는 그대로 추가
                result.append(char)
        
        return ''.join(result)
    except Exception as e:
        logger.error(f"초성 추출 중 오류 발생: {str(e)}", exc_info=True)
        return None

def is_chosung_query(query: str) -> bool:
    """
    쿼리가 초성으로만 이루어져 있는지 확인
    
    Args:
        query (str): 검색 쿼리
        
    Returns:
        bool: 초성으로만 이루어진 쿼리이면 True, 아니면 False
    """
    if not query:
        return False
    
    # 공백을 제외한 모든 문자가 초성인지 확인
    for char in query:
        if char != ' ' and char not in CHOSUNG_SET:
            return False
    
    return True

def has_korean(text: str) -> bool:
    """
    텍스트에 한글이 포함되어 있는지 확인
    초성 문자도 한글로 인식함
    
    Args:
        text (str): 확인할 텍스트
        
    Returns:
        bool: 한글이 포함되어 있으면 True, 아니면 False
    """
    if not text:
        return False
    
    for char in text:
        if '가' <= char <= '힣' or char in CHOSUNG_SET:
            return True
    
    return False