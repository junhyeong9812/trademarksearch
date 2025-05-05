"""
상표 조회수 관련 서비스

이 모듈은 상표 조회수 증가 기능을 제공합니다.
"""
from loguru import logger
from elasticsearch import NotFoundError

from app.core.elasticsearch import es_client
from app.core.config import settings
from app.core.exceptions import SearchQueryError, IndexNotFoundError, ElasticsearchConnectionError

async def increment_view_count(pid: str) -> bool:
    """
    상표 조회수 증가
    
    Args:
        pid (str): 상표 고유 ID
        
    Returns:
        bool: 성공 여부
        
    Raises:
        IndexNotFoundError: 인덱스를 찾을 수 없는 경우
        ElasticsearchConnectionError: Elasticsearch 연결 오류
        SearchQueryError: 검색 쿼리 오류
    """
    index_name = settings.ELASTICSEARCH_INDEX
    
    try:
        # 현재 조회수 조회
        response = es_client.search(
            index=index_name,
            body={
                "query": {
                    "term": {
                        "pid": pid
                    }
                },
                "_source": ["viewCount"]
            }
        )
        
        hits = response["hits"]["hits"]
        if not hits:
            logger.warning(f"상표를 찾을 수 없음 - pid: {pid}")
            return False
        
        # 현재 조회수
        current_view_count = hits[0]["_source"].get("viewCount", 0)
        new_view_count = current_view_count + 1
        
        # 조회수 업데이트
        update_response = es_client.update(
            index=index_name,
            id=hits[0]["_id"],
            body={
                "doc": {
                    "viewCount": new_view_count
                }
            },
            refresh=True
        )
        
        logger.debug(f"조회수 증가: {pid}, {current_view_count} -> {new_view_count}")
        
        return update_response["result"] == "updated"
    
    except NotFoundError as e:
        logger.error(f"인덱스 '{index_name}'를 찾을 수 없습니다")
        raise IndexNotFoundError(index_name)
    
    except ConnectionError as e:
        logger.error(f"Elasticsearch 연결 오류: {str(e)}")
        raise ElasticsearchConnectionError()
    
    except Exception as e:
        logger.error(f"조회수 증가 실행 오류: {str(e)}", exc_info=True)
        raise SearchQueryError(detail=str(e))