# 상표 도메인 패키지 초기화
# 상표 관련 주요 모델, 스키마, 함수 등을 편의를 위해 임포트

# 모델 임포트
from app.domain.trademark.models.trademark_base import TrademarkBase

# 스키마 임포트
from app.domain.trademark.schemas.trademark_response import TrademarkResponse
from app.domain.trademark.schemas.trademark_search_params import TrademarkSearchParams
from app.domain.trademark.schemas.trademark_detail_response import TrademarkDetailResponse
from app.domain.trademark.schemas.autocomplete_schema import AutocompleteResponse, AutocompleteSuggestion

# 인덱스 관련 함수 및 매핑 임포트
from app.domain.trademark.index.trademark_mapping import trademark_mapping
from app.domain.trademark.index.create_trademark_index import create_trademark_index

# 서비스 함수 임포트
from app.domain.trademark.services.load_trademark_data import load_trademark_data
from app.domain.trademark.services.search_trademarks import search_trademarks
from app.domain.trademark.services.process_trademark_data import process_trademark_data
from app.domain.trademark.services.chosung_utils import extract_chosung, is_chosung_query, has_korean
from app.domain.trademark.services.pronunciation_utils import english_to_korean_pronunciation
from app.domain.trademark.services.trademark_detail_service import get_trademark_by_pid, get_trademark_by_application_number
from app.domain.trademark.services.view_count_service import increment_view_count
from app.domain.trademark.services.pid_utils import generate_next_pid, is_valid_pid

# 외부로 노출할 모듈 목록
__all__ = [
    'TrademarkBase',               # 기본 도메인 모델
    'TrademarkResponse',           # 응답 스키마
    'TrademarkSearchParams',       # 검색 매개변수 스키마
    'TrademarkDetailResponse',     # 상세 정보 응답 스키마
    'AutocompleteResponse',        # 자동완성 응답 스키마
    'AutocompleteSuggestion',      # 자동완성 제안 스키마
    'trademark_mapping',           # ES 인덱스 매핑
    'create_trademark_index',      # 인덱스 생성 함수
    'load_trademark_data',         # 데이터 로드 함수
    'search_trademarks',           # 검색 함수
    'process_trademark_data',      # 데이터 처리 함수
    'extract_chosung',             # 초성 추출 함수
    'is_chosung_query',            # 초성 쿼리 여부 확인 함수
    'has_korean',                  # 한글 포함 여부 확인 함수
    'english_to_korean_pronunciation', # 영어 -> 한글 발음 변환 함수
    'get_trademark_by_pid',        # pid로 상표 조회 함수
    'get_trademark_by_application_number', # 출원번호로 상표 조회 함수
    'increment_view_count',        # 조회수 증가 함수
    'generate_next_pid',           # 다음 pid 생성 함수
    'is_valid_pid'                 # pid 유효성 검사 함수
]
