"""
상표 인덱스 생성 함수

이 모듈은 Elasticsearch에 상표 데이터 인덱스를 생성하는 함수를 제공합니다.
"""
import logging
from app.core.elasticsearch import es_client
from app.core.config import settings
from app.domain.trademark.index.trademark_mapping import trademark_mapping

logger = logging.getLogger(__name__)

def create_trademark_index():
    """
    상표 데이터 인덱스 생성
    
    DB_INIT_MODE 설정에 따라 다르게 동작:
    - create: 기존 인덱스 삭제 후 새로 생성
    - update: 인덱스가 없으면 생성, 있으면 유지
    - none: 아무 작업 안함
    """
    index_name = settings.ELASTICSEARCH_INDEX
    
    # DB 초기화 모드 확인
    init_mode = settings.DB_INIT_MODE.lower()
    
    # none 모드면 아무 작업 안함
    if init_mode == "none":
        logger.info(f"DB 초기화 모드가 'none'이므로 인덱스 작업을 건너뜁니다.")
        return
    
    # 인덱스 존재 여부 확인
    index_exists = es_client.indices.exists(index=index_name)
    
    # create 모드이고 인덱스가 존재하면 삭제
    if init_mode == "create" and index_exists:
        try:
            logger.info(f"DB 초기화 모드가 'create'이므로 기존 인덱스 '{index_name}'를 삭제합니다.")
            es_client.indices.delete(index=index_name)
            index_exists = False
            logger.info(f"인덱스 '{index_name}' 삭제 완료")
        except Exception as e:
            logger.error(f"인덱스 '{index_name}' 삭제 실패: {str(e)}")
            raise e
    
    # update 모드이고 인덱스가 존재하면 유지
    if init_mode == "update" and index_exists:
        logger.info(f"인덱스 '{index_name}'가 이미 존재하고 DB 초기화 모드가 'update'이므로 유지합니다.")
        return
    
    # 인덱스가 없거나 create 모드인 경우 새로 생성
    if not index_exists:
        try:
            logger.info(f"인덱스 '{index_name}'를 생성합니다.")
            response = es_client.indices.create(
                index=index_name,
                body=trademark_mapping
            )
            logger.info(f"인덱스 '{index_name}' 생성 성공: {response}")
        except Exception as e:
            logger.error(f"인덱스 '{index_name}' 생성 실패: {str(e)}")
            raise e