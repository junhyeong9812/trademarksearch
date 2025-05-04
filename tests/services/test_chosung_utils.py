"""
초성 유틸리티 함수 테스트 모듈

이 모듈은 한글 초성 추출 및 초성 검색 유틸리티 함수를 테스트합니다.
"""
import pytest
from app.domain.trademark.services.chosung_utils import extract_chosung, is_chosung_query, has_korean

def test_extract_chosung():
    """초성 추출 함수 테스트"""
    # 기본 케이스
    assert extract_chosung("프레스카") == "ㅍㄹㅅㅋ"
    assert extract_chosung("간호사 타이쿤") == "ㄱㅎㅅ ㅌㅇㅋ"
    assert extract_chosung("한글처리") == "ㅎㄱㅊㄹ"
    
    # 한글 + 다른 문자
    assert extract_chosung("ABC테스트123") == "ABCㅌㅅㅌ123"
    assert extract_chosung("Hello 월드!") == "Hello ㅇㄷ!"
    
    # 특수 케이스
    assert extract_chosung("") == ""
    assert extract_chosung(None) is None
    
    # 자음과 모음 처리
    assert extract_chosung("ㄱㄴㄷㄹ") == "ㄱㄴㄷㄹ"  # 이미 초성인 경우
    assert extract_chosung("가나다라") == "ㄱㄴㄷㄹ"
    assert extract_chosung("갉갉갉") == "ㄱㄱㄱ"      # 받침이 있는 경우
    
    # 복합 케이스
    assert extract_chosung("상표-2023") == "ㅅㅍ-2023"
    assert extract_chosung("안녕! 반가워~") == "ㅇㄴ! ㅂㄱㅇ~"

def test_is_chosung_query():
    """초성 쿼리 확인 함수 테스트"""
    # 초성만 있는 케이스
    assert is_chosung_query("ㄱㄴㄷ") == True
    assert is_chosung_query("ㅅㅈ") == True
    assert is_chosung_query("ㄱㄴ ㄷㄹ") == True   # 공백이 있는 경우
    
    # 초성이 아닌 케이스
    assert is_chosung_query("가나다") == False
    assert is_chosung_query("ABC") == False
    assert is_chosung_query("ㄱㄴ다라") == False  # 초성과 한글이 섞인 경우
    assert is_chosung_query("ㄱ123") == False    # 초성과 숫자가 섞인 경우
    
    # 예외 케이스
    assert is_chosung_query("") == False
    assert is_chosung_query(None) == False

def test_has_korean():
    """한글 포함 확인 함수 테스트"""
    # 한글이 있는 케이스
    assert has_korean("가나다") == True
    assert has_korean("ABC가나다") == True
    assert has_korean("123 한글 포함") == True
    
    # 초성도 한글로 인식해야 함
    assert has_korean("ㄱㄴㄷ") == True
    
    # 한글이 없는 케이스
    assert has_korean("ABC") == False
    assert has_korean("123") == False
    assert has_korean("!@#") == False
    
    # 예외 케이스
    assert has_korean("") == False
    assert has_korean(None) == False

@pytest.mark.parametrize("input_text,expected_chosung", [
    ("프레스카", "ㅍㄹㅅㅋ"),
    ("간호사 타이쿤", "ㄱㅎㅅ ㅌㅇㅋ"),
    ("스마일게이트", "ㅅㅁㅇㄱㅇㅌ"),
    ("삼성전자", "ㅅㅅㅈㅈ"),
    ("엘지전자", "ㅇㅈㅈㅈ"),
    ("현대자동차", "ㅎㄷㅈㄷㅊ"),
    ("카카오", "ㅋㅋㅇ"),
    ("네이버", "ㄴㅇㅂ"),
])
def test_extract_chosung_parametrized(input_text, expected_chosung):
    """파라미터화된 초성 추출 테스트"""
    assert extract_chosung(input_text) == expected_chosung

def test_mixed_cases():
    """복합 케이스 테스트 (초성 + 일반 검색)"""
    # 상표명을 초성으로 변환
    test_brands = [
        ("삼성전자", "ㅅㅅㅈㅈ"),
        ("현대자동차", "ㅎㄷㅈㄷㅊ"),
        ("엘지전자", "ㅇㅈㅈㅈ"),
    ]
    
    for brand, chosung in test_brands:
        # 해당 브랜드명이 초성인지 확인
        assert is_chosung_query(brand) == False
        assert is_chosung_query(chosung) == True
        
        # 해당 브랜드명에서 추출한 초성과 기대값이 일치하는지 확인
        assert extract_chosung(brand) == chosung