"""
상표 데이터 로드 및 색인 함수

이 모듈은 JSON 파일에서 상표 데이터를 로드하고 Elasticsearch에 색인하는 함수를 제공합니다.
"""
import json
import logging
from typing import Dict, Any
from elasticsearch.helpers import bulk

from app.core.elasticsearch import es_client
from app.core.config import settings
from app.domain.trademark.services.process_trademark_data import process_trademark_data

logger = logging.getLogger(__name__)

async def load_trademark_data(file_path: str) -> Dict[str, int]:
    """상표 데이터 JSON 파일 로드 및 Elasticsearch에 색인"""
    try:
        # 우선 인덱스 존재 여부 확인
        index_name = settings.ELASTICSEARCH_INDEX
        if not es_client.indices.exists(index=index_name):
            from app.domain.trademark.index.create_trademark_index import create_trademark_index
            create_trademark_index()
            logger.info(f"인덱스 '{index_name}'를 새로 생성했습니다.")
        
        # 이미 데이터가 있는 경우 create 모드면 삭제
        if settings.DB_INIT_MODE.lower() == "create":
            try:
                # 기존 문서 삭제 쿼리
                es_client.delete_by_query(
                    index=index_name,
                    body={"query": {"match_all": {}}},
                    refresh=True
                )
                logger.info(f"DB 초기화 모드가 'create'이므로 기존 문서를 모두 삭제했습니다.")
            except Exception as e:
                logger.error(f"기존 문서 삭제 실패: {str(e)}")
        
        # JSON 파일 로드
        with open(file_path, 'r', encoding='utf-8') as f:
            trademarks = json.load(f)
        
        logger.info(f"총 {len(trademarks)}개의 상표 데이터를 로드했습니다.")
        
        # 상표 데이터 전처리 및 색인 작업 생성
        actions = []
        for tm in trademarks:
            processed_tm = process_trademark_data(tm)
            
            # 색인 작업 추가
            actions.append({
                "_index": index_name,
                "_source": processed_tm
            })
        
        # 벌크 색인 실행
        success, failed = bulk(es_client, actions, refresh=True)
        logger.info(f"색인 완료: {success}개 성공, {failed}개 실패")
        
        return {"success": success, "failed": failed}
    
    except Exception as e:
        logger.error(f"상표 데이터 로드 실패: {str(e)}")
        raise e