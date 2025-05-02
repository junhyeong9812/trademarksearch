"""
커스텀 예외 클래스들

이 모듈은 상표 검색 API에서 사용할 커스텀 예외 클래스들을 정의합니다.
"""
from fastapi import HTTPException


class TrademarkAPIException(HTTPException):
    """상표 API 기본 예외 클래스"""
    pass


class ElasticsearchConnectionError(TrademarkAPIException):
    """Elasticsearch 연결 오류"""
    def __init__(self, detail: str = "Elasticsearch 연결에 실패했습니다"):
        super().__init__(status_code=503, detail=detail)


class IndexNotFoundError(TrademarkAPIException):
    """인덱스를 찾을 수 없음 오류"""
    def __init__(self, index_name: str):
        super().__init__(
            status_code=404, 
            detail=f"인덱스 '{index_name}'를 찾을 수 없습니다"
        )


class DataLoadingError(TrademarkAPIException):
    """데이터 로딩 오류"""
    def __init__(self, detail: str = "데이터 로딩에 실패했습니다"):
        super().__init__(status_code=500, detail=detail)


class SearchQueryError(TrademarkAPIException):
    """검색 쿼리 오류"""
    def __init__(self, detail: str = "검색 쿼리 처리에 실패했습니다"):
        super().__init__(status_code=400, detail=detail)


class InvalidParameterError(TrademarkAPIException):
    """잘못된 매개변수 오류"""
    def __init__(self, detail: str = "유효하지 않은 매개변수입니다"):
        super().__init__(status_code=422, detail=detail)


class FileNotFoundError(TrademarkAPIException):
    """파일을 찾을 수 없음 오류"""
    def __init__(self, file_path: str):
        super().__init__(
            status_code=404, 
            detail=f"파일 '{file_path}'를 찾을 수 없습니다"
        )