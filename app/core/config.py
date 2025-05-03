import os
from dotenv import load_dotenv

# 디버깅: 현재 작업 디렉토리 확인
print(f"[DEBUG] 현재 작업 디렉토리: {os.getcwd()}")

# .env.dev 파일 경로 확인
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env.dev")
print(f"[DEBUG] .env.dev 경로: {env_path}")
print(f"[DEBUG] .env.dev 존재 여부: {os.path.exists(env_path)}")

# .env.dev 파일 로드
load_dotenv(dotenv_path=".env.dev", override=True)

# 디버깅: 로드된 환경 변수 확인
print(f"[DEBUG] ELASTICSEARCH_HOST: {os.getenv('ELASTICSEARCH_HOST')}")
print(f"[DEBUG] ELASTICSEARCH_PORT: {os.getenv('ELASTICSEARCH_PORT')}")

# 기본 환경변수 설정
class Settings:
    PROJECT_NAME: str = "상표 검색 API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Elasticsearch 설정
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT: int = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    ELASTICSEARCH_INDEX: str = os.getenv("ELASTICSEARCH_INDEX", "trademarks")
    
    def __init__(self):
        # 디버깅: 실제 설정된 값 확인
        print(f"[DEBUG] Settings.ELASTICSEARCH_HOST: {self.ELASTICSEARCH_HOST}")
        print(f"[DEBUG] Settings.ELASTICSEARCH_PORT: {self.ELASTICSEARCH_PORT}")
    
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