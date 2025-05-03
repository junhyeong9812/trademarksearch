"""
데이터 처리 서비스 테스트 모듈
"""
import pytest
from app.domain.trademark.services.process_trademark_data import process_trademark_data
from app.domain.trademark.services.helpers import format_date, process_list_field

def test_process_trademark_data():
    """상표 데이터 전처리 테스트"""
    raw_data = {
        "productName": "테스트상표",
        "applicationDate": "20230101",
        "registrationNumber": "12345678",
        "registrationDate": ["20230301", "20230302"],
        "asignProductMainCodeList": "42",
        "viennaCodeList": "null",
        "priorityClaimDateList": ["null", "20230303"],
        "someNullField": None
    }
    
    processed = process_trademark_data(raw_data)
    
    # 날짜 형식 변환 확인
    assert processed["applicationDate"] == "2023-01-01"
    assert processed["registrationDate"] == ["2023-03-01", "2023-03-02"]
    
    # 리스트 필드 처리 확인
    assert processed["registrationNumber"] == ["12345678"]
    assert processed["asignProductMainCodeList"] == ["42"]
    assert processed["viennaCodeList"] is None
    assert processed["priorityClaimDateList"] == ["2023-03-03"]
    
    # null 처리 확인
    assert processed["someNullField"] is None

def test_format_date():
    """날짜 포맷 변환 테스트"""
    # 정상적인 날짜 변환
    assert format_date("20230101") == "2023-01-01"
    assert format_date("20231225") == "2023-12-25"
    
    # 특수 케이스
    assert format_date("null") is None
    assert format_date("") is None
    assert format_date(None) is None
    assert format_date("invalid") is None  # 잘못된 형식
    assert format_date("202301") is None  # 너무 짧은 형식
    assert format_date("202301010") is None  # 너무 긴 형식

def test_process_list_field():
    """리스트 필드 처리 테스트"""
    # 리스트 그대로 반환
    assert process_list_field([1, 2, 3]) == [1, 2, 3]
    assert process_list_field(["a", "b", "c"]) == ["a", "b", "c"]
    
    # 단일 값을 리스트로 변환
    assert process_list_field("single_value") == ["single_value"]
    assert process_list_field(42) == [42]
    
    # null 처리
    assert process_list_field(None) is None
    assert process_list_field("null") is None
    
    # 빈 리스트
    assert process_list_field([]) == []

def test_edge_cases():
    """엣지 케이스 처리 테스트"""
    # 빈 데이터
    empty_data = {}
    processed = process_trademark_data(empty_data)
    assert processed == {}
    
    # 모든 값이 null인 데이터
    null_data = {
        "productName": None,
        "applicationDate": "null",
        "registrationNumber": None
    }
    processed = process_trademark_data(null_data)
    
    assert processed["productName"] is None
    assert processed["applicationDate"] is None
    assert processed["registrationNumber"] is None
    
    # 복잡한 중첩 구조
    complex_data = {
        "registrationDate": ["20230101", "null", "20230301"],
        "priorityClaimDateList": [None, "null", "20230303"]
    }
    processed = process_trademark_data(complex_data)
    
    assert processed["registrationDate"] == ["2023-01-01", "2023-03-01"]
    assert processed["priorityClaimDateList"] == ["2023-03-03"]