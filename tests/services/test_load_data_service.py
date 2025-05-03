"""
데이터 로드 서비스 테스트 모듈
"""
import pytest
import json
import os

from app.domain.trademark.services.load_trademark_data import load_trademark_data
from app.core.exceptions import FileNotFoundError, DataLoadingError
from app.core.config import settings

@pytest.mark.asyncio
async def test_load_data_file_not_found():
    """존재하지 않는 파일 로드 시 예외 테스트"""
    with pytest.raises(Exception):
        await load_trademark_data("non_existent_file.json")

@pytest.mark.asyncio
async def test_load_data_success(tmp_path, create_test_index):
    """데이터 로드 성공 테스트"""
    # 테스트 인덱스 생성
    create_test_index()
    
    # 테스트 JSON 파일 생성
    test_data = [
        {
            "productName": "테스트 상표1",
            "applicationNumber": "40-2023-0000001",
            "applicationDate": "20230101"
        },
        {
            "productName": "테스트 상표2",
            "applicationNumber": "40-2023-0000002",
            "applicationDate": "20230102"
        }
    ]
    
    test_file = tmp_path / "test_data.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f)
    
    # 데이터 로드 실행
    result = await load_trademark_data(str(test_file))
    
    assert result["success"] == 2
    assert result["failed"] == 0

@pytest.mark.asyncio
async def test_load_data_with_invalid_data(tmp_path, create_test_index):
    """잘못된 형식의 데이터 로드 테스트"""
    create_test_index()
    
    # 잘못된 형식의 데이터
    test_data = [
        {"productName": "정상 데이터"},
        {"productName": "잘못된 데이터", "applicationDate": "invalid_date"}
    ]
    
    test_file = tmp_path / "invalid_data.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f)
    
    # 데이터 로드 실행 (에러가 발생해도 계속 진행해야 함)
    result = await load_trademark_data(str(test_file))
    
    # 최소한 일부는 성공해야 함
    assert result["success"] > 0

@pytest.mark.asyncio
async def test_load_data_update_mode(tmp_path, create_test_index, index_test_data):
    """DB 초기화 모드에 따른 데이터 로드 테스트"""
    create_test_index()
    
    # 기존 데이터 인덱싱
    existing_data = {"productName": "기존 상표", "applicationNumber": "40-2022-0000001"}
    index_test_data(existing_data)
    
    # 새로운 데이터 파일 생성
    new_data = [{"productName": "새로운 상표", "applicationNumber": "40-2023-0000001"}]
    test_file = tmp_path / "new_data.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f)
    
    # DB_INIT_MODE를 'update'로 변경
    original_mode = settings.DB_INIT_MODE
    settings.DB_INIT_MODE = "update"
    
    try:
        # 데이터 로드
        result = await load_trademark_data(str(test_file))
        
        # update 모드에서는 기존 데이터가 유지되어야 함
        from app.core.elasticsearch import es_client
        count = es_client.count(index=settings.ELASTICSEARCH_INDEX)["count"]
        assert count == 2  # 기존 1개 + 새로운 1개
        
    finally:
        settings.DB_INIT_MODE = original_mode