# 인덱스 패키지 초기화
from app.domain.trademark.index.trademark_mapping import trademark_mapping
from app.domain.trademark.index.create_trademark_index import create_trademark_index

__all__ = ['trademark_mapping', 'create_trademark_index']