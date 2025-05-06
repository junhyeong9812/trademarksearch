"""
상표 검색 함수

이 모듈은 검색 매개변수에 따라 상표 데이터를 검색하는 함수를 제공합니다.
초성 검색 및 발음 변환 기능이 포함되어 있습니다.
"""
from typing import Dict, Any, List
from elasticsearch import NotFoundError
from loguru import logger

from app.core.elasticsearch import es_client
from app.core.config import settings
from app.domain.trademark.schemas.trademark_search_params import TrademarkSearchParams, SortOption
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
            "filter": [],
            "should": []
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
            # 초성 검색인 경우 - 한글 상표명과 영문 상표명 발음의 초성 모두 검색
            logger.debug(f"초성 검색 모드 적용: {query_text}")
            
            query["bool"]["should"] = [
                # 한글 상표명 초성 검색
                {
                    "match_phrase_prefix": {
                        "productName_chosung": {
                            "query": query_text,
                            "boost": 5.0
                        }
                    }
                },
                # 영문 상표명 한글 발음 초성 검색 (추가된 부분)
                {
                    "match_phrase_prefix": {
                        "productNameEngPronunciation_chosung": {
                            "query": query_text,
                            "boost": 4.0
                        }
                    }
                }
            ]
            query["bool"]["minimum_should_match"] = 1
        else:
            # 일반 검색인 경우 - should 절 구성
            should_clauses = []
            
            # 1. 한글 상표명 검색 (null이 아닌 경우)
            should_clauses.append({
                "bool": {
                    "must": [
                        {
                            "exists": {
                                "field": "productName"
                            }
                        },
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["productName^3", "productName.ngram^2"],
                                "type": "best_fields"
                            }
                        }
                    ]
                }
            })
            
            # 2. 영문 상표명 검색 (null이 아닌 경우)
            should_clauses.append({
                "bool": {
                    "must": [
                        {
                            "exists": {
                                "field": "productNameEng"
                            }
                        },
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["productNameEng^2", "productNameEng.ngram"],
                                "type": "best_fields"
                            }
                        }
                    ]
                }
            })
            
            # 3. 영문 상표명의 한글 발음 검색 (null이 아닌 경우)
            should_clauses.append({
                "bool": {
                    "must": [
                        {
                            "exists": {
                                "field": "productNameEngPronunciation"
                            }
                        },
                        {
                            "match": {
                                "productNameEngPronunciation": {
                                    "query": query_text,
                                    "boost": 2.5  # 발음 일치에 가중치 부여
                                }
                            }
                        }
                    ]
                }
            })
            
            # 4. 영문 상표명의 한글 발음 초성 검색 (null이 아닌 경우) - 추가된 부분
            should_clauses.append({
                "bool": {
                    "must": [
                        {
                            "exists": {
                                "field": "productNameEngPronunciation_chosung"
                            }
                        },
                        {
                            "match": {
                                "productNameEngPronunciation_chosung": {
                                    "query": query_text,
                                    "boost": 2.0
                                }
                            }
                        }
                    ]
                }
            })
            
            # 최소 하나의 should 절이 매칭되어야 함
            query["bool"]["should"] = should_clauses
            query["bool"]["minimum_should_match"] = 1
            
            # 한글이 포함된 경우 초성 필드도 부분적으로 검색
            if has_korean_chars:
                logger.debug(f"한글 포함 - 초성 부분 검색도 활성화")
                query["bool"]["should"].append({
                    "match": {
                        "productName_chosung": {
                            "query": query_text,
                            "boost": 1.0
                        }
                    }
                })
                # 영문 상표명 한글 발음의 초성도 검색 - 추가된 부분
                query["bool"]["should"].append({
                    "match": {
                        "productNameEngPronunciation_chosung": {
                            "query": query_text,
                            "boost": 0.8
                        }
                    }
                })
        
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
    
    # 정렬 처리
    sort_list = build_sort_options(search_params.sort)
    logger.debug(f"정렬 옵션: {sort_list}")
    
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
                "sort": sort_list,
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
                        },
                        "productNameEng": {
                            "number_of_fragments": 0,
                            "pre_tags": ["<mark>"],
                            "post_tags": ["</mark>"]
                        },
                        "productNameEngPronunciation": {
                            "number_of_fragments": 0,
                            "pre_tags": ["<mark>"],
                            "post_tags": ["</mark>"]
                        },
                        "productNameEngPronunciation_chosung": {
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

def build_sort_options(sort_options: List[SortOption] = None) -> List[Dict]:
    """
    정렬 옵션 목록을 Elasticsearch 정렬 형식으로 변환

    Args:
        sort_options (List[SortOption], optional): 정렬 옵션 목록

    Returns:
        List[Dict]: Elasticsearch 정렬 형식
    """
    # 기본 정렬 옵션: 스코어 내림차순
    default_sort = [
        {"_score": {"order": "desc"}},
        {"pid": {"order": "asc"}}  # pid로 2차 정렬
    ]

    if not sort_options:
        return default_sort

    es_sort = []

    for option in sort_options:
        # Elasticsearch 8.x 이상에서는 null_value 설정을 허용하지 않거나 제한하므로 제거
        # 날짜 필드인 경우 format 지정
        if option.field in ["applicationDate", "registrationDate"]:
            sort_option = {
                option.field: {
                    "order": option.order,
                    "format": "yyyy-MM-dd"
                }
            }
        else:
            sort_option = {
                option.field: {
                    "order": option.order
                }
            }

        es_sort.append(sort_option)

    # pid로 2차 정렬 항상 추가
    es_sort.append({"pid": {"order": "asc"}})

    return es_sort