"""
상표 상세 조회 서비스

이 모듈은 상표 상세 정보 조회 기능을 제공합니다.
"""
from loguru import logger
from elasticsearch import NotFoundError

from app.core.elasticsearch import es_client
from app.core.config import settings
from app.core.exceptions import SearchQueryError, IndexNotFoundError, ElasticsearchConnectionError

async def get_trademark_by_pid(pid: str) -> dict:
    """
    상표 고유 ID로 상표 정보 조회
    
    Args:
        pid (str): 상표 고유 ID
        
    Returns:
        dict: 상표 정보
        
    Raises:
        IndexNotFoundError: 인덱스를 찾을 수 없는 경우
        ElasticsearchConnectionError: Elasticsearch 연결 오류
        SearchQueryError: 검색 쿼리 오류
    """
    index_name = settings.ELASTICSEARCH_INDEX
    
    try:
        response = es_client.search(
            index=index_name,
            body={
                "query": {
                    "term": {
                        "pid": pid
                    }
                },
                "_source": True
            }
        )
        
        hits = response["hits"]["hits"]
        if not hits:
            logger.warning(f"상표를 찾을 수 없음 - pid: {pid}")
            return None
        
        # 첫 번째 결과 반환
        return hits[0]["_source"]
    
    except NotFoundError as e:
        logger.error(f"인덱스 '{index_name}'를 찾을 수 없습니다")
        raise IndexNotFoundError(index_name)
    
    except ConnectionError as e:
        logger.error(f"Elasticsearch 연결 오류: {str(e)}")
        raise ElasticsearchConnectionError()
    
    except Exception as e:
        logger.error(f"상표 조회 실행 오류: {str(e)}", exc_info=True)
        raise SearchQueryError(detail=str(e))


async def get_trademark_by_application_number(application_number: str) -> dict:
    """
    출원번호로 상표 정보 조회
    
    Args:
        application_number (str): 상표 출원번호
        
    Returns:
        dict: 상표 정보
        
    Raises:
        IndexNotFoundError: 인덱스를 찾을 수 없는 경우
        ElasticsearchConnectionError: Elasticsearch 연결 오류
        SearchQueryError: 검색 쿼리 오류
    """
    index_name = settings.ELASTICSEARCH_INDEX
    
    try:
        response = es_client.search(
            index=index_name,
            body={
                "query": {
                    "term": {
                        "applicationNumber": application_number
                    }
                },
                "_source": True
            }
        )
        
        hits = response["hits"]["hits"]
        if not hits:
            logger.warning(f"상표를 찾을 수 없음 - 출원번호: {application_number}")
            return None
        
        # 첫 번째 결과 반환
        return hits[0]["_source"]
    
    except NotFoundError as e:
        logger.error(f"인덱스 '{index_name}'를 찾을 수 없습니다")
        raise IndexNotFoundError(index_name)
    
    except ConnectionError as e:
        logger.error(f"Elasticsearch 연결 오류: {str(e)}")
        raise ElasticsearchConnectionError()
    
    except Exception as e:
        logger.error(f"상표 조회 실행 오류: {str(e)}", exc_info=True)
        raise SearchQueryError(detail=str(e))