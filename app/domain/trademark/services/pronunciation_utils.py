"""
발음 변환 유틸리티 함수

이 모듈은 영어 텍스트를 한글 발음으로 변환하는 함수를 제공합니다.
g2pk 라이브러리를 사용하여 영어 텍스트를 한글 발음으로 변환합니다.
"""
from loguru import logger
import re
from typing import Optional

try:
    # g2pk(그래프 투 포네틱 코리안) 라이브러리 임포트
    from g2pk import G2p
    g2p = G2p()
    G2PK_AVAILABLE = True
except ImportError:
    logger.warning("g2pk 라이브러리를 찾을 수 없습니다. 기본 발음 변환만 사용합니다.")
    g2p = None
    G2PK_AVAILABLE = False

def english_to_korean_pronunciation(text: str) -> Optional[str]:
    """
    영어 텍스트를 한글 발음으로 변환
    
    Args:
        text (str): 변환할 영어 텍스트
        
    Returns:
        Optional[str]: 한글 발음, 변환 실패 시 None
    """
    if text is None or not text:
        return None
    
    # 소문자로 변환
    text_lower = text.lower()
    
    # 특수 문자 제거
    text_clean = re.sub(r'[^\w\s]', '', text_lower)
    
    # 단어 분리
    words = text_clean.split()
    result = []
    
    for word in words:
        # g2pk 라이브러리를 사용한 자동 변환
        if G2PK_AVAILABLE and g2p:
            try:
                korean_pron = g2p(word, 'eng')
                result.append(korean_pron)
            except Exception as e:
                logger.error(f"g2pk 변환 오류: {str(e)}, 단어: {word}")
                # 변환 실패 시 기본 변환 규칙 적용
                result.append(basic_eng_to_kor_pronunciation(word))
        else:
            # g2pk 사용 불가능한 경우 기본 변환 규칙 적용
            result.append(basic_eng_to_kor_pronunciation(word))
    
    # 결과 조합
    return ' '.join(result)

def basic_eng_to_kor_pronunciation(word: str) -> str:
    """
    기본 영한 발음 변환 규칙 (g2pk 없을 때 사용)
    
    Args:
        word (str): 변환할 영어 단어
        
    Returns:
        str: 한글 발음으로 변환된 결과
    """
    # 기본 변환 규칙 (간단한 매핑)
    eng_to_kor = {
        'a': '에이', 'b': '비', 'c': '시', 'd': '디', 'e': '이', 
        'f': '에프', 'g': '지', 'h': '에이치', 'i': '아이', 'j': '제이', 
        'k': '케이', 'l': '엘', 'm': '엠', 'n': '엔', 'o': '오', 
        'p': '피', 'q': '큐', 'r': '알', 's': '에스', 't': '티', 
        'u': '유', 'v': '브이', 'w': '더블유', 'x': '엑스', 'y': '와이', 'z': '지'
    }
    
    # 단어를 구성하는 각 문자별로 변환 (매우 기본적인 방식)
    result = ''
    for char in word:
        if char in eng_to_kor:
            result += eng_to_kor[char]
        else:
            result += char
    
    return result