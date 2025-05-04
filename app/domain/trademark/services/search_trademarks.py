"""
상표 검색 함수

이 모듈은 검색 매개변수에 따라 상표 데이터를 검색하는 함수를 제공합니다.
초성 검색 기능이 포함되어 있습니다.
"""
from typing import Dict, Any
from elasticsearch import NotFoundError
from loguru import logger

from app.core.elasticsearch import es_client
from app.core.config import settings
from app.domain.trademark.schemas.trademark_search_params import TrademarkSearchParams
from app.core.exceptions import SearchQueryError, IndexNotFoundError, ElasticsearchConnectionError
from app.domain.trademark.services.chosung_utils import is_chosung_query, has_korean

async def search_trademarks(search_params: TrademarkSearchParams) -> Dict[str, Any]:
    """
    검색 매개변수에 따라 상표 데이터 검색
    
    Args:
        search_params (TrademarkSearchParams): 검색 매개변수
        
    Returns:
        Dict[str, Any]: 검색 결과
        
    Raises:
        IndexNotFoundError: 인덱스를 찾을 수 없는 경우
        ElasticsearchConnectionError: Elasticsearch 연결 오류
        SearchQueryError: 검색 쿼리 오류
    """
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
        query_text = search_params.query.strip()
        
        # 초성 검색 여부 확인
        chosung_only = is_chosung_query(query_text)
        has_korean_chars = has_korean(query_text)
        
        logger.debug(f"쿼리 분석 - 초성 전용: {chosung_only}, 한글 포함: {has_korean_chars}")
        
        if chosung_only:
            # 초성 검색인 경우
            logger.debug(f"초성 검색 모드 적용: {query_text}")
            query["bool"]["must"].append({
                "match_phrase_prefix": {
                    "productName_chosung": {
                        "query": query_text,
                        "boost": 5.0
                    }
                }
            })
        else:
            # 일반 검색인 경우
            query["bool"]["must"].append({
                "multi_match": {
                    "query": query_text,
                    "fields": ["productName^3", "productName.ngram^2", "productNameEng^2", "productNameEng.ngram"],
                    "type": "best_fields"
                }
            })
            
            # 한글이 포함된 경우 초성 필드도 부분적으로 검색
            if has_korean_chars:
                logger.debug(f"한글 포함 - 초성 부분 검색도 활성화")
                query["bool"]["should"] = [{
                    "match": {
                        "productName_chosung": {
                            "query": query_text,
                            "boost": 1.0
                        }
                    }
                }]
        
        logger.debug(f"검색어 적용: {query_text}")
    
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
        logger.debug(f"최종 쿼리: {query}")
        
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
                "_source": True,
                "highlight": {
                    "fields": {
                        "productName": {
                            "number_of_fragments": 0,
                            "pre_tags": ["<mark>"],
                            "post_tags": ["</mark>"]
                        },
                        "productName_chosung": {
                            "number_of_fragments": 0,
                            "pre_tags": ["<mark>"],
                            "post_tags": ["</mark>"]
                        }
                    }
                }
            }
        )
        
        # 검색 결과 처리
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        
        logger.debug(f"검색 결과 - 총 {total}개")
        
        results = []
        for hit in hits:
            source = hit["_source"]
            
            # 하이라이트 정보 추가
            if "highlight" in hit:
                source["highlight"] = hit["highlight"]
            
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