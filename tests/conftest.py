"""
테스트 픽스처 및 설정 파일

이 모듈은 테스트를 위한 픽스처들을 정의합니다.
"""
import pytest
import asyncio
import os
import sys
from httpx import AsyncClient
from fastapi.testclient import TestClient

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 환경 변수 강제 설정
os.environ["ELASTICSEARCH_HOST"] = "127.0.0.1"  # localhost 대신 127.0.0.1 사용
os.environ["ELASTICSEARCH_PORT"] = "9200"

from app.main import app
from app.core.config import settings
from app.core.elasticsearch import es_client
from app.domain.trademark.services.chosung_utils import extract_chosung

@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_client():
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """비동기 HTTP 테스트 클라이언트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
async def setup_test_database():
    """테스트용 데이터베이스 설정"""
    # 테스트용 인덱스 이름으로 변경
    test_index = f"{settings.ELASTICSEARCH_INDEX}_test"
    original_index = settings.ELASTICSEARCH_INDEX
    settings.ELASTICSEARCH_INDEX = test_index
    
    try:
        # 테스트 인덱스 삭제 (있다면)
        if es_client.indices.exists(index=test_index):
            es_client.indices.delete(index=test_index)
        
        yield
        
    finally:
        # 테스트 인덱스 정리
        if es_client.indices.exists(index=test_index):
            es_client.indices.delete(index=test_index)
        
        # 원래 인덱스 이름 복구
        settings.ELASTICSEARCH_INDEX = original_index

@pytest.fixture
def sample_trademark_data():
    """샘플 상표 데이터"""
    return {
        "productName": "테스트 상표명",
        "productNameEng": "Test Trademark",
        "applicationNumber": "40-2023-0000001",
        "applicationDate": "20230101",
        "registerStatus": "등록",
        "publicationNumber": "20230101",
        "publicationDate": "20230101",
        "registrationNumber": ["12345678"],
        "registrationDate": ["20230101"],
        "asignProductMainCodeList": ["42"],
        "asignProductSubCodeList": ["4223"]
    }

@pytest.fixture
def create_test_index():
    """테스트용 인덱스 생성 픽스처"""
    def _create_index():
        from app.domain.trademark.index.create_trademark_index import create_trademark_index
        create_trademark_index()
    return _create_index

@pytest.fixture
def index_test_data():
    """테스트 데이터 인덱싱 헬퍼"""
    def _index_data(data, refresh=True):
        # 초성 필드가 없고 productName이 있으면 추가
        if "productName" in data and "productName_chosung" not in data:
            data["productName_chosung"] = extract_chosung(data["productName"])
            
        index_name = settings.ELASTICSEARCH_INDEX
        return es_client.index(
            index=index_name,
            body=data,
            refresh=refresh
        )
    return _index_data

@pytest.fixture
def mock_search_result():
    """검색 결과 모킹"""
    def _set_search_result(data_list):
        # 실제 환경에서는 이 함수는 사용되지 않고 실제 Elasticsearch 검색이 수행됩니다
        pass
    return _set_search_result

@pytest.fixture
def sample_chosung_data():
    """초성 검색 테스트를 위한 샘플 데이터"""
    return [
        {
            "productName": "삼성전자",
            "productNameEng": "Samsung Electronics",
            "applicationNumber": "40-2023-0001001",
            "applicationDate": "20230101",
            "registerStatus": "등록",
            "productName_chosung": "ㅅㅅㅈㅈ"
        },
        {
            "productName": "엘지전자",
            "productNameEng": "LG Electronics",
            "applicationNumber": "40-2023-0001002",
            "applicationDate": "20230102",
            "registerStatus": "등록",
            "productName_chosung": "ㅇㅈㅈㅈ"
        },
        {
            "productName": "애플",
            "productNameEng": "Apple",
            "applicationNumber": "40-2023-0001003",
            "applicationDate": "20230103",
            "registerStatus": "등록",
            "productName_chosung": "ㅇㅍ"
        },
        {
            "productName": "구글",
            "productNameEng": "Google",
            "applicationNumber": "40-2023-0001004",
            "applicationDate": "20230104",
            "registerStatus": "등록",
            "productName_chosung": "ㄱㄱ"
        }
    ]