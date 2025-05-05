"""
상표 검색에 최적화된 완전한 인덱스 매핑

초성 검색 기능, 발음 변환 기능이 포함된 매핑 전략
"""
import logging

logger = logging.getLogger(__name__)

# 상표 데이터 인덱스 매핑 정의
trademark_mapping = {
    "mappings": {
        "properties": {
            # 고유 ID (pid) 및 조회수 필드 추가
            "pid": {
                "type": "keyword"
            },
            "viewCount": {
                "type": "integer",
                "null_value": 0
            },
            
            # 상표명 필드 (한글/영문) - 다중 분석기 활용
            "productName": {
                "type": "text",
                "analyzer": "nori_standard",  # 기본 검색용
                "search_analyzer": "nori_search",  # 검색 시 사용
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    },
                    "ngram": {
                        "type": "text", 
                        "analyzer": "nori_ngram",
                        "search_analyzer": "nori_search_ngram"
                    },
                    "edge_ngram": {
                        "type": "text",
                        "analyzer": "nori_edge_ngram",
                        "search_analyzer": "korean_standard"
                    },
                    "no_decompound": {
                        "type": "text",
                        "analyzer": "nori_no_decompound"
                    }
                }
            },
            # 상표명 초성 필드 (초성 검색용)
            "productName_chosung": {
                "type": "text",
                "analyzer": "keyword",
                "search_analyzer": "keyword"
            },
            "productNameEng": {
                "type": "text",
                "analyzer": "english_standard",
                "search_analyzer": "english_search",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    },
                    "ngram": {
                        "type": "text",
                        "analyzer": "english_ngram", 
                        "search_analyzer": "english_search_ngram"
                    }
                }
            },
            # 영문 상표명의 한글 발음 필드 추가
            "productNameEngPronunciation": {
                "type": "text",
                "analyzer": "nori_standard",
                "search_analyzer": "nori_search",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            
            # 출원/등록 번호 필드들
            "applicationNumber": {
                "type": "keyword",
                "fields": {
                    "search": {
                        "type": "text",
                        "analyzer": "number_analyzer"
                    }
                }
            },
            "registrationNumber": {
                "type": "keyword",
                "fields": {
                    "search": {
                        "type": "text",
                        "analyzer": "number_analyzer"
                    }
                }
            },
            "publicationNumber": {
                "type": "keyword"
            },
            "internationalRegNumbers": {
                "type": "keyword"
            },
            "priorityClaimNumList": {
                "type": "keyword"
            },
            
            # 날짜 필드들
            "applicationDate": {
                "type": "date", 
                "format": "yyyyMMdd||yyyy-MM-dd||strict_date_optional_time"
            },
            "publicationDate": {
                "type": "date", 
                "format": "yyyyMMdd||yyyy-MM-dd||strict_date_optional_time"
            },
            "registrationDate": {
                "type": "date", 
                "format": "yyyyMMdd||yyyy-MM-dd||strict_date_optional_time"
            },
            "internationalRegDate": {
                "type": "date", 
                "format": "yyyyMMdd||yyyy-MM-dd||strict_date_optional_time"
            },
            "priorityClaimDateList": {
                "type": "date", 
                "format": "yyyyMMdd||yyyy-MM-dd||strict_date_optional_time"
            },
            
            # 상태 정보
            "registerStatus": {
                "type": "keyword",
                "fields": {
                    "text": {
                        "type": "text",
                        "analyzer": "korean_standard"
                    }
                }
            },
            
            # 코드 정보 필드들
            "asignProductMainCodeList": {
                "type": "keyword",
                "fields": {
                    "search": {
                        "type": "text",
                        "analyzer": "number_analyzer"
                    }
                }
            },
            "asignProductSubCodeList": {
                "type": "keyword",
                "fields": {
                    "search": {
                        "type": "text",
                        "analyzer": "number_analyzer"
                    }
                }
            },
            "viennaCodeList": {
                "type": "keyword"
            }
        }
    },
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "max_ngram_diff": 9,
            "refresh_interval": "5s"
        },
        "analysis": {
            "analyzer": {
                # 한국어 기본 분석기
                "nori_standard": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer_standard",
                    "filter": [
                        "nori_readingform",
                        "nori_part_of_speech_filter",
                        "lowercase",
                        "trim"
                    ]
                },
                # 한국어 검색용 분석기 (오타 허용)
                "nori_search": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer_standard",
                    "filter": [
                        "nori_readingform",
                        "lowercase",
                        "trim",
                        "asciifolding"
                    ]
                },
                # 한국어 n-gram 분석기
                "nori_ngram": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer_standard",
                    "filter": [
                        "lowercase",
                        "nori_readingform",
                        "ngram_filter"
                    ]
                },
                # 한국어 n-gram 검색용 분석기
                "nori_search_ngram": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer_standard",
                    "filter": [
                        "lowercase",
                        "nori_readingform"
                    ]
                },
                # 한국어 edge n-gram 분석기
                "nori_edge_ngram": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer_standard",
                    "filter": [
                        "lowercase",
                        "nori_readingform",
                        "edge_ngram_filter"
                    ]
                },
                # 복합어 미분리 분석기
                "nori_no_decompound": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer_none",
                    "filter": [
                        "lowercase",
                        "nori_readingform"
                    ]
                },
                # 영문 기본 분석기
                "english_standard": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "trim"
                    ]
                },
                # 영문 검색용 분석기
                "english_search": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "trim"
                    ]
                },
                # 영문 n-gram 분석기
                "english_ngram": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_ngram_filter"
                    ]
                },
                # 영문 n-gram 검색용 분석기
                "english_search_ngram": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase"
                    ]
                },
                # 번호/코드용 분석기
                "number_analyzer": {
                    "type": "custom",
                    "tokenizer": "keyword",
                    "filter": ["lowercase", "trim"]
                },
                # 기본 한국어 분석기
                "korean_standard": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer_standard",
                    "filter": ["lowercase"]
                }
            },
            "tokenizer": {
                # 한글 토크나이저 (discard 모드)
                "nori_tokenizer_standard": {
                    "type": "nori_tokenizer",
                    "decompound_mode": "discard"
                },
                # 한글 토크나이저 (분리 안함)
                "nori_tokenizer_none": {
                    "type": "nori_tokenizer",
                    "decompound_mode": "none"
                }
            },
            "filter": {
                # n-gram 필터
                "ngram_filter": {
                    "type": "ngram",
                    "min_gram": 2,
                    "max_gram": 5
                },
                # edge n-gram 필터
                "edge_ngram_filter": {
                    "type": "edge_ngram", 
                    "min_gram": 1,
                    "max_gram": 10
                },
                # 영문 n-gram 필터
                "english_ngram_filter": {
                    "type": "ngram",
                    "min_gram": 2,
                    "max_gram": 10
                },
                # 품사 필터
                "nori_part_of_speech_filter": {
                    "type": "nori_part_of_speech",
                    "stoptags": [
                        "E", "IC", "J", "MAG", "MAJ", "MM", "SP", 
                        "SSC", "SSO", "SC", "SE", "XPN", "XSA", "XSN", "XSV"
                    ]
                }
            }
        }
    }
}