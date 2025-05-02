"""
상표 검색 함수

이 모듈은 검색 매개변수에 따라 상표 데이터를 검색하는 함수를 제공합니다.
"""
from typing import Dict, Any
from elasticsearch import NotFoundError
from loguru import logger

from app.core.elasticsearch import es_client
from app.core.config import settings
from app.domain.trademark.schemas.trademark_search_params import TrademarkSearchParams
from app.core.exceptions import SearchQueryError, IndexNotFoundError, ElasticsearchConnectionError

async def search_trademarks(search_params: TrademarkSearchParams) -> Dict[str, Any]:
    """검색 매개변수에 따라 상표 데이터 검색"""
    index_name = settings.ELASTICSEARCH_INDEX
    
    logger.debug(f"검색 시작 - 인덱스: {index_name}, 검색어: {search_params.query}")
    
    # 기본 검색 쿼리 구성
    query = {
        "bool": {
            "must": [],
            "filter": []
        }
    }
    
    # 검색어 처리
    if search_params.query:
        query["bool"]["must"].append({
            "multi_match": {
                "query": search_params.query,
                "fields": ["productName^3", "productName.ngram^2", "productNameEng^2", "productNameEng.ngram"],
                "type": "best_fields"
            }
        })
        logger.debug(f"검색어 적용: {search_params.query}")
    
    # 상태 필터
    if search_params.status:
        query["bool"]["filter"].append({
            "term": {"registerStatus": search_params.status}
        })
        logger.debug(f"상태 필터 적용: {search_params.status}")
    
    # 상품 주 분류 코드 필터
    if search_params.main_code:
        query["bool"]["filter"].append({
            "term": {"asignProductMainCodeList": search_params.main_code}
        })
        logger.debug(f"주 분류 코드 필터 적용: {search_params.main_code}")
    
    # 상품 유사군 코드 필터
    if search_params.sub_code:
        query["bool"]["filter"].append({
            "term": {"asignProductSubCodeList": search_params.sub_code}
        })
        logger.debug(f"유사군 코드 필터 적용: {search_params.sub_code}")
    
    # 날짜 범위 필터
    if search_params.start_date or search_params.end_date:
        date_range = {}
        if search_params.start_date:
            date_range["gte"] = search_params.start_date.isoformat()
        if search_params.end_date:
            date_range["lte"] = search_params.end_date.isoformat()
        
        query["bool"]["filter"].append({
            "range": {"applicationDate": date_range}
        })
        logger.debug(f"날짜 범위 필터 적용: {date_range}")
    
    # 페이징 처리
    from_idx = (search_params.page - 1) * search_params.size
    
    try:
        logger.debug(f"Elasticsearch 검색 실행 - 페이지: {search_params.page}, 사이즈: {search_params.size}")
        
        # 검색 실행
        response = es_client.search(
            index=index_name,
            body={
                "query": query,
                "from": from_idx,
                "size": search_params.size,
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"applicationDate": {"order": "desc"}}
                ],
                "_source": True
            }
        )
        
        # 검색 결과 처리
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        
        logger.debug(f"검색 결과 - 총 {total}개")
        
        results = []
        for hit in hits:
            source = hit["_source"]
            # Pydantic 모델로 변환
            results.append(source)
        
        return {
            "total": total,
            "page": search_params.page,
            "size": search_params.size,
            "results": results
        }
    
    except NotFoundError as e:
        logger.error(f"인덱스 '{index_name}'를 찾을 수 없습니다")
        raise IndexNotFoundError(index_name)
    
    except ConnectionError as e:
        logger.error(f"Elasticsearch 연결 오류: {str(e)}")
        raise ElasticsearchConnectionError()
    
    except Exception as e:
        logger.error(f"상표 검색 실행 오류: {str(e)}", exc_info=True)
        raise SearchQueryError(detail=str(e))