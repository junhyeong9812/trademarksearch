from elasticsearch import Elasticsearch
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_elasticsearch_client() -> Elasticsearch:
    """Elasticsearch 클라이언트 연결 설정 및 반환"""
    es_host = f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"
    
    try:
        es_client = Elasticsearch([es_host])
        info = es_client.info()
        logger.info(f"Elasticsearch 연결 성공: {info['version']['number']}")
        return es_client
    except Exception as e:
        logger.error(f"Elasticsearch 연결 실패: {str(e)}")
        raise e

# 글로벌 Elasticsearch 클라이언트 인스턴스
es_client = get_elasticsearch_client()