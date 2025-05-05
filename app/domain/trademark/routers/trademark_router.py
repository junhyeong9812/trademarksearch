"""
상표 검색 API 라우터

이 모듈은 상표 검색 관련 API 엔드포인트들을 정의합니다.
RESTful API 설계 원칙에 따라 리소스 중심으로 구성되었습니다.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from loguru import logger

from app.domain.trademark.schemas.trademark_search_params import TrademarkSearchParams, SortOption, SortField, SortOrder
from app.domain.trademark.schemas.trademark_response import TrademarkResponse
from app.domain.trademark.schemas.trademark_detail_response import TrademarkDetailResponse
from app.domain.trademark.schemas.autocomplete_schema import AutocompleteResponse
from app.domain.trademark.services.search_trademarks import search_trademarks
from app.domain.trademark.services.load_trademark_data import load_trademark_data
from app.domain.trademark.services.autocomplete_service import get_autocomplete_suggestions
from app.domain.trademark.services.view_count_service import increment_view_count
from app.domain.trademark.services.trademark_detail_service import get_trademark_by_application_number
from app.core.exceptions import (
    SearchQueryError,
    DataLoadingError,
    IndexNotFoundError,
    InvalidParameterError
)

router = APIRouter(prefix="/api/trademarks", tags=["trademarks"])


@router.get("/", response_model=TrademarkResponse)
async def search_trademark_endpoint(
    query: str = Query(None, description="검색어 (상표명)"),
    status: str = Query(None, description="상표 등록 상태"),
    main_code: str = Query(None, description="상품 주 분류 코드"),
    sub_code: str = Query(None, description="상품 유사군 코드"),
    start_date: str = Query(None, description="검색 시작일 (YYYY-MM-DD)"),
    end_date: str = Query(None, description="검색 종료일 (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 결과 수"),
    sort_field: Optional[List[str]] = Query(None, description="정렬 필드 (예: applicationDate,productName)"),
    sort_order: Optional[List[str]] = Query(None, description="정렬 방향 (asc 또는 desc)"),
) -> TrademarkResponse:
    """상표 검색 API"""
    try:
        logger.info(f"상표 검색 요청 - 검색어: '{query}', 페이지: {page}")
        
        # 정렬 옵션 처리
        sort_options = None
        if sort_field:
            sort_options = []
            # sort_order가 없거나 길이가 다른 경우 기본값 처리
            if not sort_order:
                sort_order = ["desc"] * len(sort_field)
            elif len(sort_order) < len(sort_field):
                sort_order.extend(["desc"] * (len(sort_field) - len(sort_order)))
            
            for i, field in enumerate(sort_field):
                try:
                    sort_field_enum = SortField(field)
                    sort_order_enum = SortOrder(sort_order[i].lower())
                    sort_options.append(SortOption(field=sort_field_enum, order=sort_order_enum))
                except ValueError as e:
                    logger.warning(f"잘못된 정렬 옵션: {field}, {sort_order[i]}")
                    raise InvalidParameterError(f"잘못된 정렬 옵션: {field}, {sort_order[i]}")
        
        # 검색 매개변수 생성
        search_params = TrademarkSearchParams(
            query=query,
            status=status,
            main_code=main_code,
            sub_code=sub_code,
            start_date=start_date,
            end_date=end_date,
            page=page,
            size=size,
            sort=sort_options
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
    except InvalidParameterError as e:
        logger.error(f"잘못된 매개변수 오류: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"예상치 못한 검색 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_endpoint(
    query: str = Query(..., min_length=1, description="검색어"),
    size: int = Query(10, ge=1, le=20, description="반환할 제안 수")
) -> AutocompleteResponse:
    """상표명 자동완성 API
    
    초성 검색, 오타 교정, n-gram 기반 유사 문자열 매칭, 영문 발음 변환 기능을 지원합니다.
    """
    try:
        logger.info(f"자동완성 요청 - 검색어: '{query}', 크기: {size}")
        
        result = await get_autocomplete_suggestions(query, size)
        
        logger.info(f"자동완성 완료 - {result.total}개 제안")
        
        return result
    
    except SearchQueryError as e:
        logger.error(f"자동완성 쿼리 오류: {str(e)}")
        raise e
    except IndexNotFoundError as e:
        logger.error(f"인덱스 없음 오류: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"예상치 못한 자동완성 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.get("/{application_number}", response_model=TrademarkDetailResponse)
async def get_trademark_detail(
    application_number: str = Path(..., description="상표 출원번호"),
    increment_count: bool = Query(True, description="조회수 증가 여부")
) -> TrademarkDetailResponse:
    """상표 상세 정보 조회 API
    
    상표 출원번호로 상표 상세 정보를 조회합니다.
    increment_count가 True이면 조회수도 함께 증가시킵니다.
    """
    try:
        logger.info(f"상표 상세 조회 요청 - 출원번호: {application_number}")
        
        # 상표 정보 조회
        trademark = await get_trademark_by_application_number(application_number)
        
        if not trademark:
            logger.warning(f"상표를 찾을 수 없음 - 출원번호: {application_number}")
            raise HTTPException(status_code=404, detail=f"출원번호가 '{application_number}'인 상표를 찾을 수 없습니다")
        
        # 조회수 증가 (요청된 경우)
        if increment_count and "pid" in trademark:
            pid = trademark["pid"]
            success = await increment_view_count(pid)
            if success:
                # 조회수 업데이트 (UI에 표시하기 위해)
                trademark["viewCount"] = trademark.get("viewCount", 0) + 1
                logger.debug(f"조회수 증가 성공 - pid: {pid}, 현재 조회수: {trademark['viewCount']}")
        
        logger.info(f"상표 상세 조회 완료 - 출원번호: {application_number}")
        
        return TrademarkDetailResponse(data=trademark)
    
    except IndexNotFoundError as e:
        logger.error(f"인덱스 없음 오류: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"예상치 못한 상표 상세 조회 오류: {str(e)}", exc_info=True)
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