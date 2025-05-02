import os
from dotenv import load_dotenv

# .env 파일 로드
# load_dotenv()

# .env.dev 파일 로드
load_dotenv(dotenv_path=".env.dev")

# 기본 환경변수 설정
class Settings:
    PROJECT_NAME: str = "상표 검색 API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Elasticsearch 설정
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT: int = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    ELASTICSEARCH_INDEX: str = os.getenv("ELASTICSEARCH_INDEX", "trademarks")
    
    # DB 초기화 설정 (create, update, none)
    DB_INIT_MODE: str = os.getenv("DB_INIT_MODE", "create")
    
    # 데이터 로드 설정 (auto, manual)
    DATA_LOAD_MODE: str = os.getenv("DATA_LOAD_MODE", "auto")
    
    # 데이터 파일 경로
    DATA_FILE_PATH: str = os.getenv("DATA_FILE_PATH", "data/trademark_sample.json")
    
    # 페이징 기본값 설정
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

# 전역 설정 인스턴스
settings = Settings()