"""
상표 검색 API 애플리케이션 진입점

이 모듈은 FastAPI 애플리케이션을 초기화하고 구성합니다.
"""
import logging
import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.elasticsearch import es_client
from app.domain.trademark.index.create_trademark_index import create_trademark_index

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="상표 데이터를 검색하고 필터링할 수 있는 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청 처리 시간 미들웨어
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """요청 처리 시간을 측정하여 응답 헤더에 추가하는 미들웨어"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.debug(f"처리 시간: {process_time:.4f}초, 경로: {request.url.path}")
    return response

# 전역 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """예기치 않은 예외를 처리하는 전역 핸들러"""
    logger.error(f"예기치 않은 예외: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "내부 서버 오류가 발생했습니다.", "detail": str(exc)},
    )

@app.get("/")
def read_root():
    """API 루트 경로 핸들러"""
    return {
        "message": f"{settings.PROJECT_NAME}에 오신 것을 환영합니다.",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "api_prefix": "/api"
    }

@app.get("/health")
def health_check():
    """API 헬스 체크 엔드포인트"""
    try:
        # Elasticsearch 연결 확인
        es_info = es_client.info()
        
        # 인덱스 확인
        index_exists = es_client.indices.exists(index=settings.ELASTICSEARCH_INDEX)
        
        # 문서 수 확인
        count = 0
        if index_exists:
            count = es_client.count(index=settings.ELASTICSEARCH_INDEX)["count"]
        
        return {
            "status": "healthy",
            "elasticsearch": {
                "status": "connected",
                "version": es_info['version']['number'],
                "index_exists": index_exists,
                "document_count": count
            },
            "configuration": {
                "db_init_mode": settings.DB_INIT_MODE,
                "data_load_mode": settings.DATA_LOAD_MODE
            }
        }
    except Exception as e:
        logger.error(f"헬스 체크 실패: {str(e)}")
        return {
            "status": "unhealthy",
            "detail": str(e)
        }

# 애플리케이션 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트 핸들러"""
    logger.info(f"{settings.PROJECT_NAME} 애플리케이션 시작")
    
    try:
        # Elasticsearch 연결 확인
        es_info = es_client.info()
        logger.info(f"Elasticsearch 연결 성공: {es_info['version']['number']}")
        
        # 인덱스 초기화 (DB_INIT_MODE에 따라 동작)
        logger.info(f"DB 초기화 모드: {settings.DB_INIT_MODE}")
        create_trademark_index()
        
        # 데이터 자동 로드 (auto 모드인 경우)
        if settings.DATA_LOAD_MODE.lower() == "auto":
            logger.info("데이터 로드 모드가 'auto'로 설정되어 있어 데이터를 자동으로 로드합니다.")
            
            # 데이터 파일 경로 확인
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                settings.DATA_FILE_PATH
            )
            
            if not os.path.exists(file_path):
                logger.error(f"데이터 파일을 찾을 수 없습니다: {file_path}")
            else:
                try:
                    # 인덱스에 데이터가 있는지 확인
                    index_name = settings.ELASTICSEARCH_INDEX
                    if es_client.indices.exists(index=index_name):
                        count = es_client.count(index=index_name)["count"]
                        
                        # DB_INIT_MODE가 update이고 이미 데이터가 있으면 건너뜀
                        if settings.DB_INIT_MODE.lower() == "update" and count > 0:
                            logger.info(f"DB 초기화 모드가 'update'이고 이미 {count}개의 문서가 있으므로 데이터 로드를 건너뜁니다.")
                            return
                    
                    # 데이터 로드 실행
                    from app.domain.trademark.services.load_trademark_data import load_trademark_data
                    result = await load_trademark_data(file_path)
                    logger.info(f"데이터 로드 완료: {result['success']}개 성공, {result['failed']}개 실패")
                except Exception as e:
                    logger.error(f"데이터 로드 실패: {str(e)}")
        else:
            logger.info("데이터 로드 모드가 'manual'로 설정되어 있어 데이터를 자동으로 로드하지 않습니다.")
            logger.info("데이터를 로드하려면 'python -m app.scripts.load_data' 명령을 실행하세요.")
            
    except Exception as e:
        logger.error(f"애플리케이션 시작 중 오류 발생: {str(e)}", exc_info=True)

# 애플리케이션 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행되는 이벤트 핸들러"""
    logger.info(f"{settings.PROJECT_NAME} 애플리케이션 종료")

# API 라우터 가져오기 및 등록
# 라우터 구현 후 주석 해제
# from app.domain.trademark.routers import trademark_router
# app.include_router(trademark_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)