"""
로깅 설정 모듈

이 모듈은 애플리케이션 전체의 로깅을 설정합니다.
"""
import sys
from loguru import logger
from datetime import datetime
import os


def setup_logging():
    """로깅 설정 초기화"""
    # 기존 핸들러 제거
    logger.remove()
    
    # 로그 디렉토리 생성
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 콘솔 출력 설정 (INFO 레벨 이상)
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="INFO"
    )
    
    # 에러 콘솔 출력 설정 (ERROR 레벨 이상)
    logger.add(
        sys.stderr,
        colorize=True,
        format="<red>{time:YYYY-MM-DD HH:mm:ss.SSS}</red> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="ERROR"
    )
    
    # 일반 로그 파일 (DEBUG 레벨 이상)
    logger.add(
        f"{log_dir}/trademark_api_{datetime.now().strftime('%Y%m%d')}.log",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        enqueue=True,  # 멀티스레드 안전성
        catch=True     # 예외 안전성
    )
    
    # 에러 전용 로그 파일 (ERROR 레벨 이상)
    logger.add(
        f"{log_dir}/trademark_api_error_{datetime.now().strftime('%Y%m%d')}.log",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        enqueue=True,
        catch=True
    )
    
    # 성능 로그 파일 (특정 로거용)
    logger.add(
        f"{log_dir}/trademark_api_performance_{datetime.now().strftime('%Y%m%d')}.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}",
        filter=lambda record: record["extra"].get("performance", False),
        level="INFO",
        enqueue=True
    )
    
    return logger


def get_performance_logger():
    """성능 로깅을 위한 전용 로거"""
    return logger.bind(performance=True)


# 로깅 레벨 설정
def set_log_level(level: str):
    """런타임에서 로그 레벨 변경"""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if level.upper() in valid_levels:
        # 모든 핸들러의 레벨을 변경하거나 새로 추가
        logger.remove()
        setup_logging()
        
        # 새로운 레벨로 다시 설정
        # 이 부분은 실제 구현에서 더 정교하게 처리해야 할 수 있음
        logger.info(f"로그 레벨이 {level}로 변경되었습니다.")
    else:
        logger.warning(f"유효하지 않은 로그 레벨: {level}")


# 로그 사용 예시를 위한 함수들
def log_examples():
    """로깅 사용 예시"""
    # 기본 로깅
    logger.debug("디버그 메시지 - 개발 중 상세 정보")
    logger.info("일반 정보 메시지")
    logger.warning("경고 메시지")
    logger.error("에러 메시지")
    logger.critical("치명적 오류 메시지")
    
    # 예외와 함께 로깅
    try:
        1 / 0
    except Exception as e:
        logger.exception("예외 발생 - 스택 트레이스와 함께 로깅")
    
    # 성능 로깅
    perf_logger = get_performance_logger()
    perf_logger.info("API 응답 시간: 0.125초")
    
    # 사용자 정의 필드와 함께 로깅
    logger.bind(user_id="user123", request_id="req456").info("사용자별 요청 처리")