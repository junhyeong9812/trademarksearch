"""
상표 인덱스 매핑 정의

이 모듈은 Elasticsearch에서 상표 데이터를 저장할 인덱스의 매핑을 정의합니다.
"""
import logging

logger = logging.getLogger(__name__)

# 상표 데이터 인덱스 매핑 정의
trademark_mapping = {
    "mappings": {
        "properties": {
            # 상표명 필드 (한글/영문)
            "productName": {
                "type": "text",
                "analyzer": "nori",  # 한국어 형태소 분석기 사용
                "fields": {
                    "keyword": {"type": "keyword"},  # 정확히 일치하는 검색을 위한 키워드 필드
                    "ngram": {  # 부분 검색을 위한 n-gram 필드
                        "type": "text",
                        "analyzer": "standard"  
                    }
                }
            },
            "productNameEng": {
                "type": "text",
                "analyzer": "standard",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngram": {
                        "type": "text",
                        "analyzer": "standard"
                    }
                }
            },
            
            # 출원/등록 번호
            "applicationNumber": {"type": "keyword"},
            "registrationNumber": {"type": "keyword"},
            "publicationNumber": {"type": "keyword"},
            "internationalRegNumbers": {"type": "keyword"},
            "priorityClaimNumList": {"type": "keyword"},
            
            # 날짜 필드들
            "applicationDate": {"type": "date", "format": "yyyyMMdd||yyyy-MM-dd"},
            "publicationDate": {"type": "date", "format": "yyyyMMdd||yyyy-MM-dd"},
            "registrationDate": {"type": "date", "format": "yyyyMMdd||yyyy-MM-dd"},
            "internationalRegDate": {"type": "date", "format": "yyyyMMdd||yyyy-MM-dd"},
            "priorityClaimDateList": {"type": "date", "format": "yyyyMMdd||yyyy-MM-dd"},
            
            # 상태 정보
            "registerStatus": {"type": "keyword"},
            
            # 코드 정보
            "asignProductMainCodeList": {"type": "keyword"},
            "asignProductSubCodeList": {"type": "keyword"},
            "viennaCodeList": {"type": "keyword"}
        }
    },
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "analysis": {
            "analyzer": {
                "nori_analyzer": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer",
                    "filter": ["lowercase", "trim", "nori_part_of_speech"]
                }
            },
            "tokenizer": {
                "nori_tokenizer": {
                    "type": "nori_tokenizer",
                    "decompound_mode": "mixed"
                }
            },
            "filter": {
                "nori_part_of_speech": {
                    "type": "nori_part_of_speech",
                    "stoptags": ["E", "IC", "J", "MAG", "MAJ", "MM", "SP", "SSC", "SSO", "SC", "SE", "XPN", "XSA", "XSN", "XSV"]
                }
            }
        }
    }
}