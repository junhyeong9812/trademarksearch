"""
상표 검색 API 라우터

이 모듈은 상표 검색 관련 API 엔드포인트들을 정의합니다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from app.domain.trademark.schemas.trademark_search_params import TrademarkSearchParams
from app.domain.trademark.schemas.trademark_response import TrademarkResponse
from app.domain.trademark.services.search_trademarks import search_trademarks
from app.domain.trademark.services.load_trademark_data import load_trademark_data
from app.core.exceptions import (
    SearchQueryError,
    DataLoadingError,
    IndexNotFoundError,
    InvalidParameterError
)

router = APIRouter(prefix="/api/trademarks", tags=["trademarks"])


@router.get("/search", response_model=TrademarkResponse)
async def search_trademark_endpoint(
    query: str = Query(None, description="검색어 (상표명)"),
    status: str = Query(None, description="상표 등록 상태"),
    main_code: str = Query(None, description="상품 주 분류 코드"),
    sub_code: str = Query(None, description="상품 유사군 코드"),
    start_date: str = Query(None, description="검색 시작일 (YYYY-MM-DD)"),
    end_date: str = Query(None, description="검색 종료일 (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 결과 수")
) -> TrademarkResponse:
    """상표 검색 API"""
    try:
        logger.info(f"상표 검색 요청 - 검색어: '{query}', 페이지: {page}")
        
        # 검색 매개변수 생성
        search_params = TrademarkSearchParams(
            query=query,
            status=status,
            main_code=main_code,
            sub_code=sub_code,
            start_date=start_date,
            end_date=end_date,
            page=page,
            size=size
        )
        
        # 검색 실행
        result = await search_trademarks(search_params)
        
        logger.info(f"검색 완료 - 총 {result['total']}개 결과")
        
        return TrademarkResponse(**result)
    
    except SearchQueryError as e:
        logger.error(f"검색 쿼리 오류: {str(e)}")
        raise e
    except IndexNotFoundError as e:
        logger.error(f"인덱스 없음 오류: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"예상치 못한 검색 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.post("/load-data")
async def load_data_endpoint(file_path: str = Query(..., description="데이터 파일 경로")):
    """데이터 수동 로드 API"""
    try:
        logger.info(f"데이터 로드 요청 - 파일 경로: {file_path}")
        
        result = await load_trademark_data(file_path)
        
        logger.info(f"데이터 로드 완료: {result['success']}개 성공, {result['failed']}개 실패")
        
        return {
            "message": "데이터 로드가 완료되었습니다",
            "success": result['success'],
            "failed": result['failed']
        }
    
    except DataLoadingError as e:
        logger.error(f"데이터 로드 오류: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"예상치 못한 데이터 로드 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.get("/status")
async def check_status():
    """검색 시스템 상태 확인 API"""
    try:
        logger.info("시스템 상태 확인 요청")
        
        from app.core.elasticsearch import es_client
        from app.core.config import settings
        
        index_name = settings.ELASTICSEARCH_INDEX
        
        # Elasticsearch 연결 확인
        es_info = es_client.info()
        
        # 인덱스 확인
        index_exists = es_client.indices.exists(index=index_name)
        
        # 문서 수 확인
        count = 0
        if index_exists:
            count = es_client.count(index=index_name)["count"]
        
        status = {
            "elasticsearch": {
                "connected": True,
                "version": es_info['version']['number']
            },
            "index": {
                "name": index_name,
                "exists": index_exists,
                "document_count": count
            }
        }
        
        logger.info(f"시스템 상태: {status}")
        
        return status
    
    except Exception as e:
        logger.error(f"상태 확인 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="상태 확인에 실패했습니다")