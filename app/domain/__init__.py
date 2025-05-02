# 도메인 패키지 초기화
# 편의를 위해 자주 사용하는 클래스와 함수를 직접 노출
from app.domain.trademark import (
    TrademarkBase,
    TrademarkResponse,
    TrademarkSearchParams,
    create_trademark_index
)

__all__ = [
    'TrademarkBase',
    'TrademarkResponse',
    'TrademarkSearchParams',
    'create_trademark_index'
]