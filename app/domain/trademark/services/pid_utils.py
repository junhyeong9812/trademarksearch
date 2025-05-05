"""
상표 고유 ID(pid) 관리 유틸리티

이 모듈은 일련번호 기반의 상표 고유 ID 생성 기능을 제공합니다.
"""
from loguru import logger
from elasticsearch import NotFoundError

from app.core.elasticsearch import es_client
from app.core.config import settings

# 메모리 기반 pid 카운터 (fallback용)
_pid_counter = 1

def generate_next_pid() -> str:
    """
    다음 일련번호 기반 상표 고유 ID 생성

    일련번호 형식으로 1부터 시작하여 순차적으로 증가하는 ID 생성
    (예: "1", "2", "3", ...)

    Returns:
        str: 다음 상표 고유 ID
    """
    global _pid_counter

    try:
        index_name = settings.ELASTICSEARCH_INDEX

        # 인덱스가 존재하지 않으면 첫 번째 ID 반환
        if not es_client.indices.exists(index=index_name):
            logger.info(f"인덱스 '{index_name}'가 존재하지 않아 첫 번째 ID '1' 반환")
            return "1"

        # 현재 최대 pid 조회
        response = es_client.search(
            index=index_name,
            body={
                "size": 0,
                "aggs": {
                    "max_pid": {
                        "max": {
                            "field": "pid.keyword"
                        }
                    }
                }
            }
        )

        # 집계 결과에서 최대 pid 추출
        max_pid = response["aggregations"]["max_pid"]["value"]

        # 결과가 없거나 유효하지 않은 경우 → 메모리 fallback
        if max_pid is None or max_pid == 0:
            pid = str(_pid_counter)
            _pid_counter += 1
            logger.info(f"유효한 최대 pid가 없어 메모리 기반 첫 번째 ID '{pid}' 반환")
            return pid

        # 숫자 형태로 변환
        try:
            next_pid = str(int(max_pid) + 1)
            logger.debug(f"다음 pid 생성: {next_pid}")
            return next_pid
        except (ValueError, TypeError):
            # 현재 최대 pid가 숫자 형태가 아닌 경우 (예: UUID)
            logger.warning(f"기존 pid '{max_pid}'가 숫자 형태가 아님. 첫 번째 ID '1' 반환")
            return "1"

    except Exception as e:
        # 오류 발생 시 안전하게 메모리 기반 pid 반환
        pid = str(_pid_counter)
        _pid_counter += 1
        logger.error(f"pid 생성 중 오류 발생 → 메모리 기반 pid 반환: {pid}, 오류: {str(e)}")
        return pid

def is_valid_pid(pid: str) -> bool:
    """
    상표 고유 ID의 유효성 검사

    Args:
        pid (str): 검사할 상표 고유 ID

    Returns:
        bool: 유효한 ID인지 여부
    """
    if not pid:
        return False

    # 숫자로만 구성된 경우
    if pid.isdigit():
        return True

    # UUID 형식인 경우 (기존 데이터와의 호환성 유지)
    import re
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    if uuid_pattern.match(pid):
        return True

    return False
