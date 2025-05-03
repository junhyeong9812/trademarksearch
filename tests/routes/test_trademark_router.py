"""
상표 API 라우터 테스트

이 모듈은 상표 관련 API 엔드포인트들을 테스트합니다.
"""
import pytest
import json
import time
from fastapi import status

# 테스트용 더미 데이터 세트
TEST_DATA = [
    {
        "productName": "테스트 상표 1",
        "productNameEng": "Test Trademark 1",
        "applicationNumber": "40-2023-0000001",
        "applicationDate": "20230101",
        "registerStatus": "등록",
        "asignProductMainCodeList": ["35"],
        "asignProductSubCodeList": ["3501"]
    },
    {
        "productName": "등록 상표 2",
        "productNameEng": "Registered Mark 2",
        "applicationNumber": "40-2023-0000002",
        "applicationDate": "20230115",
        "registerStatus": "등록",
        "asignProductMainCodeList": ["42"],
        "asignProductSubCodeList": ["4223"]
    },
    {
        "productName": "출원 상표 3",
        "productNameEng": "Pending Mark 3",
        "applicationNumber": "40-2023-0000003",
        "applicationDate": "20230201",
        "registerStatus": "출원",
        "asignProductMainCodeList": ["35"],
        "asignProductSubCodeList": ["3505"]
    },
    {
        "productName": "거절 상표 4",
        "productNameEng": "Rejected Mark 4",
        "applicationNumber": "40-2023-0000004",
        "applicationDate": "20230301",
        "registerStatus": "거절",
        "asignProductMainCodeList": ["45"],
        "asignProductSubCodeList": ["4501"]
    }
]

@pytest.fixture
def setup_test_data(create_test_index, index_test_data):
    """테스트용 데이터 준비 픽스처"""
    def _setup():
        # 테스트 인덱스 생성
        create_test_index()
        
        # 더미 데이터 인덱싱 - 데이터 전처리를 적용
        from app.domain.trademark.services.process_trademark_data import process_trademark_data
        
        for data in TEST_DATA:
            # 데이터 전처리를 적용
            processed_data = process_trademark_data(data)
            index_test_data(processed_data)
        
        # 인덱싱 완료 후 잠시 대기
        import time
        time.sleep(0.5)  # Elasticsearch 인덱싱 완료 대기
        
    return _setup

@pytest.mark.asyncio
async def test_health_check(test_client):
    """헬스 체크 엔드포인트 테스트"""
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "elasticsearch" in data

@pytest.mark.asyncio
async def test_status_endpoint(test_client):
    """상태 확인 엔드포인트 테스트"""
    response = test_client.get("/api/trademarks/status")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "elasticsearch" in data
    assert "index" in data

@pytest.mark.asyncio
async def test_search_empty(test_client, create_test_index):
    """빈 검색 결과 테스트"""
    # 인덱스 먼저 생성
    create_test_index()
    
    response = test_client.get("/api/trademarks/search")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []

@pytest.mark.asyncio
async def test_search_with_query(test_client, setup_test_data):
    """검색어로 검색 테스트"""
    # 테스트 데이터 준비
    setup_test_data()
    
    # 한글 검색어로 검색
    response = test_client.get("/api/trademarks/search?query=테스트")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["productName"] == "테스트 상표 1"
    
    # 영문 검색어로 검색
    response = test_client.get("/api/trademarks/search?query=Test")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] >= 1
    # 검색 결과가 "Test"를 포함하는지 확인
    has_test = any("Test" in result.get("productNameEng", "") for result in data["results"])
    assert has_test

@pytest.mark.asyncio
async def test_search_with_status_filter(test_client, setup_test_data):
    """상태 필터로 검색 테스트"""
    setup_test_data()
    
    # "등록" 상태로 검색
    response = test_client.get("/api/trademarks/search?status=등록")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 2  # "등록" 상태는 2개
    for result in data["results"]:
        assert result["registerStatus"] == "등록"
    
    # "출원" 상태로 검색
    response = test_client.get("/api/trademarks/search?status=출원")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["registerStatus"] == "출원"

@pytest.mark.asyncio
async def test_search_with_code_filters(test_client, setup_test_data):
    """분류 코드 필터로 검색 테스트"""
    setup_test_data()
    
    # 주 분류 코드 검색
    response = test_client.get("/api/trademarks/search?main_code=35")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 2  # 코드 35는 2개
    for result in data["results"]:
        assert "35" in result["asignProductMainCodeList"]
    
    # 유사군 코드 검색
    response = test_client.get("/api/trademarks/search?sub_code=4223")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 1
    assert "4223" in data["results"][0]["asignProductSubCodeList"]

@pytest.mark.asyncio
async def test_search_with_date_range(test_client, setup_test_data):
    """날짜 범위 검색 테스트"""
    setup_test_data()
    
    # 1월 데이터만 검색
    response = test_client.get("/api/trademarks/search?start_date=2023-01-01&end_date=2023-01-31")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 2  # 1월 데이터는 2개
    
    for result in data["results"]:
        app_date = result["applicationDate"]
        # 디버깅을 위한 출력
        print(f"Received date: {app_date}")
        
        # 두 가지 형식 모두 검증
        if len(app_date) == 8 and app_date.isdigit():
            # YYYYMMDD 형식
            assert app_date.startswith("202301")
        elif len(app_date) == 10 and '-' in app_date:
            # YYYY-MM-DD 형식
            assert app_date.startswith("2023-01")
        else:
            # 예상치 못한 형식인 경우 더 자세한 디버깅
            print(f"Unexpected date format: {app_date}")
            print(f"Date length: {len(app_date)}")
            print(f"Date type: {type(app_date)}")
            assert False, f"Unexpected date format: {app_date}"

@pytest.mark.asyncio
async def test_search_complex_filters(test_client, setup_test_data):
    """복합 필터 검색 테스트"""
    setup_test_data()
    
    # 복합 조건: 등록 상태 + 35번 분류
    response = test_client.get("/api/trademarks/search?status=등록&main_code=35")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 1  # 모든 조건을 만족하는 데이터는 1개
    result = data["results"][0]
    assert result["registerStatus"] == "등록"
    assert "35" in result["asignProductMainCodeList"]

@pytest.mark.asyncio
async def test_search_pagination(test_client, setup_test_data):
    """페이지네이션 테스트"""
    setup_test_data()
    
    # 첫 번째 페이지 (크기 2)
    response = test_client.get("/api/trademarks/search?size=2&page=1")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 4  # 총 4개 데이터
    assert len(data["results"]) == 2
    assert data["page"] == 1
    assert data["size"] == 2
    
    # 두 번째 페이지
    response = test_client.get("/api/trademarks/search?size=2&page=2")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 4
    assert len(data["results"]) == 2
    assert data["page"] == 2

@pytest.mark.asyncio
async def test_search_invalid_parameters(test_client):
    """잘못된 검색 매개변수 테스트"""
    # 잘못된 페이지 번호
    response = test_client.get("/api/trademarks/search?page=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # 잘못된 크기
    response = test_client.get("/api/trademarks/search?size=-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # 너무 큰 크기
    response = test_client.get("/api/trademarks/search?size=1000")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_search_no_results(test_client, setup_test_data):
    """검색 결과 없음 테스트"""
    setup_test_data()
    
    # 존재하지 않는 검색어
    response = test_client.get("/api/trademarks/search?query=존재하지않는검색어")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []

@pytest.mark.asyncio
async def test_load_data_endpoint(test_client, tmp_path):
    """데이터 로드 엔드포인트 테스트"""
    # 임시 JSON 파일 생성
    test_data = [{"productName": "테스트", "applicationNumber": "40-2023-0000001"}]
    test_file = tmp_path / "test_data.json"
    
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f)
    
    # 데이터 로드 테스트
    response = test_client.post(f"/api/trademarks/load-data?file_path={test_file}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "message" in data
    assert data["success"] == 1
    assert isinstance(data["failed"], (int, list))