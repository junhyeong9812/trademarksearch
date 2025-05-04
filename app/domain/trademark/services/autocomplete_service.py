"""
자동완성 서비스

이 모듈은 상표명 자동완성 로직을 제공합니다.
초성 검색을 지원합니다.
"""
from typing import List, Dict, Any
from elasticsearch import NotFoundError
from loguru import logger

from app.core.elasticsearch import es_client
from app.core.config import settings
from app.domain.trademark.schemas.autocomplete_schema import AutocompleteSuggestion, AutocompleteResponse
from app.core.exceptions import SearchQueryError, IndexNotFoundError
from app.domain.trademark.services.chosung_utils import is_chosung_query, has_korean

async def get_autocomplete_suggestions(query: str, size: int = 10) -> AutocompleteResponse:
    """
    자동완성 제안 가져오기
    
    Args:
        query (str): 검색어
        size (int, optional): 반환할 제안 수. Defaults to 10.
        
    Returns:
        AutocompleteResponse: 자동완성 제안 응답
        
    Raises:
        IndexNotFoundError: 인덱스를 찾을 수 없는 경우
        SearchQueryError: 검색 쿼리 오류
    """
    index_name = settings.ELASTICSEARCH_INDEX
    
    try:
        # 쿼리 분석
        chosung_only = is_chosung_query(query)
        has_korean_chars = has_korean(query)
        
        logger.debug(f"자동완성 쿼리 분석 - 쿼리: {query}, 초성만: {chosung_only}, 한글 포함: {has_korean_chars}")
        
        # 1. 기본 검색 쿼리
        if chosung_only:
            # 초성 검색인 경우
            logger.debug(f"초성 자동완성 검색 모드 적용: {query}")
            base_query = {
                "match_phrase_prefix": {
                    "productName_chosung": {
                        "query": query,
                        "boost": 5.0
                    }
                }
            }
        else:
            # 일반 검색인 경우
            base_query = {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "productName^5",
                        "productName.ngram^3",
                        "productName.edge_ngram^2",
                        "productNameEng^3",
                        "productNameEng.ngram^2"
                    ],
                    "fuzziness": 0 if chosung_only else 1,
                    "prefix_length": 0 if chosung_only else 1,
                    "type": "best_fields"
                }
            }
        
        # 2. 한글이 포함된 일반 검색인 경우 초성 검색도 추가
        mixed_query = None
        if has_korean_chars and not chosung_only:
            logger.debug(f"한글 포함 - 초성 부분 검색도 활성화")
            mixed_query = {
                "match": {
                    "productName_chosung": {
                        "query": query,
                        "boost": 2.0
                    }
                }
            }
        
        # 3. 최종 복합 쿼리 구성
        should_clauses = [base_query]
        if mixed_query:
            should_clauses.append(mixed_query)
        
        final_query = {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1
            }
        }
        
        logger.debug(f"자동완성 최종 쿼리: {final_query}")
        
        # 4. Elasticsearch 검색 실행
        response = es_client.search(
            index=index_name,
            body={
                "query": final_query,
                "size": size,
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
                        }
                    }
                },
                "_source": ["productName", "productNameEng", "productName_chosung"],
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"productName.keyword": {"order": "asc"}}
                ]
            }
        )
        
        # 5. 결과 처리
        hits = response["hits"]["hits"]
        suggestions = []
        
        for hit in hits:
            source = hit["_source"]
            highlight = hit.get("highlight", {})
            
            # 초성 검색 결과인 경우, 원래 상표명 + 초성 정보 제공
            original_name = source.get("productName", "")
            chosung_info = source.get("productName_chosung", "")
            
            suggestion = AutocompleteSuggestion(
                text=original_name,
                productNameEng=source.get("productNameEng"),
                score=hit["_score"],
                highlight=highlight
            )
            suggestions.append(suggestion)
            
            logger.debug(f"자동완성 결과: {original_name} (초성: {chosung_info}), 점수: {hit['_score']}")
        
        return AutocompleteResponse(
            suggestions=suggestions,
            total=len(suggestions)
        )
    
    except NotFoundError:
        logger.error(f"인덱스 '{index_name}'를 찾을 수 없습니다")
        raise IndexNotFoundError(index_name)
    
    except Exception as e:
        logger.error(f"자동완성 검색 실행 오류: {str(e)}", exc_info=True)
        raise SearchQueryError(detail=str(e))