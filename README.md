# 상표 검색 API 사용 설명서

## 1. API 사용법 및 실행 방법

### 시스템 요구사항

- Docker 및 Docker Compose
- Python 3.7 이상 (로컬 개발 시)
- 가상 환경(venv)

### 설치 및 실행 방법

#### 1. Docker 설치

- **Windows**: Docker Desktop 설치
- **Linux**: Docker 및 Docker Compose 설치

#### 2. 프로젝트 실행

1. **Elasticsearch 및 Kibana 실행**:

   ```bash
   docker-compose up -d elasticsearch kibana
   ```

   - Elasticsearch는 9200 포트에서 실행됩니다
   - Kibana는 5601 포트에서 실행됩니다
   - Kibana구동 후 Elasticsearch를 실행합니다.

2. **Python 환경 설정 및 API 서버 실행** (로컬 개발용):

   ```bash
   # 가상환경 생성 및 활성화
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

   # 필요한 패키지 설치
   pip install -r requirements.txt

   # API 서버 실행
   python -m app.main

   ```

   main.py 내부에 아래와 같은 코드가 존재하기 때문에 python으로 실행

   ```
   if __name__ == "__main__":
    import uvicorn

    # 로그 레벨 설정
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    logger.info(f"로그 레벨: {log_level}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=log_level
    )
   ```

   - API 서버는 기본적으로 8000 포트에서 실행됩니다
   - 브라우저에서 `http://localhost:8000/docs`로 접속하여 Swagger 문서 확인 가능

#### 3. 상태 확인

- 서버 상태 확인: `http://localhost:8000/health`
- API 상태 확인: `http://localhost:8000/api/trademarks/status`

### API 엔드포인트

| 엔드포인트                             | 메소드 | 설명                  |
| -------------------------------------- | ------ | --------------------- |
| `/api/trademarks/`                     | GET    | 상표 검색             |
| `/api/trademarks/autocomplete`         | GET    | 상표명 자동완성       |
| `/api/trademarks/{application_number}` | GET    | 상표 상세 정보 조회   |
| `/api/trademarks/load-data`            | POST   | 데이터 수동 로드      |
| `/api/trademarks/status`               | GET    | 검색 시스템 상태 확인 |

### 검색 API 사용 예시

#### 1. 상표 검색

상세한 테스트 URL 예시는 [테스트 URL 모음](testUrl/README.md)을 참조하세요

```
GET /api/trademarks/?query=프레스카&page=1&size=10
```

요청 예시:

```
GET http://localhost:8000/api/trademarks/?query=프레스카&status=등록
```

응답 예시:

```json
{
  "total": 1,
  "page": 1,
  "size": 10,
  "results": [
    {
      "pid": "1",
      "productName": "프레스카",
      "productNameEng": "FRESCA",
      "productName_chosung": "ㅍㄹㅅㅋ",
      "productNameEngPronunciation": "프레스카",
      "productNameEngPronunciation_chosung": "ㅍㄹㅅㅋ",
      "applicationNumber": "4019950043843",
      "applicationDate": "1995-11-17",
      "registerStatus": "등록",
      "publicationNumber": "4019970001364",
      "publicationDate": "1997-01-29",
      "registrationNumber": ["4003600590000"],
      "registrationDate": ["1997-04-17"],
      "asignProductMainCodeList": ["30"],
      "asignProductSubCodeList": ["G0301", "G0303", "G0302"],
      "viewCount": 5
    }
  ]
}
```

주요 매개변수:

- `query`: 검색어 (상표명)
- `status`: 상표 등록 상태
- `main_code`: 상품 주 분류 코드
- `sub_code`: 상품 유사군 코드
- `start_date`: 검색 시작일 (YYYY-MM-DD)
- `end_date`: 검색 종료일 (YYYY-MM-DD)
- `page`: 페이지 번호
- `size`: 페이지당 결과 수
- `sort_field`: 정렬 필드 (예: applicationDate, productName)
- `sort_order`: 정렬 방향 (asc 또는 desc)

#### 2. 자동완성

```
GET /api/trademarks/autocomplete?query=프레&size=10
```

응답 예시:

```json
{
  "suggestions": [
    {
      "text": "프레스카",
      "productNameEng": "FRESCA",
      "score": 10.25,
      "highlight": {
        "productName": ["<mark>프레</mark>스카"]
      }
    }
  ],
  "total": 1
}
```

매개변수:

- `query`: 검색어
- `size`: 반환할 제안 수 (기본값: 10)

#### 3. 상표 상세 정보 조회

```
GET /api/trademarks/4019950043843
```

응답 예시:

```json
{
  "data": {
    "pid": "1",
    "productName": "프레스카",
    "productNameEng": "FRESCA",
    "productName_chosung": "ㅍㄹㅅㅋ",
    "productNameEngPronunciation": "프레스카",
    "productNameEngPronunciation_chosung": "ㅍㄹㅅㅋ",
    "applicationNumber": "4019950043843",
    "applicationDate": "1995-11-17",
    "registerStatus": "등록",
    "publicationNumber": "4019970001364",
    "publicationDate": "1997-01-29",
    "registrationNumber": ["4003600590000"],
    "registrationDate": ["1997-04-17"],
    "asignProductMainCodeList": ["30"],
    "asignProductSubCodeList": ["G0301", "G0303", "G0302"],
    "viewCount": 6
  }
}
```

매개변수:

- `application_number`: 상표 출원번호
- `increment_count`: 조회수 증가 여부 (기본값: true)

#### 4. 초성 검색 예시

```
GET /api/trademarks/?query=ㅍㄹㅅㅋ
```

응답: "프레스카" 검색 결과와 동일

#### 5. 필터링 예시

```
GET /api/trademarks/?main_code=30&sub_code=G0301&status=등록&start_date=1995-01-01&end_date=1997-12-31
```

## 2. 구현된 기능 설명

### 검색 기능

- **키워드 검색**: 상표명(한글/영문) 검색
- **초성 검색**: 한글 초성만으로 상표명 검색 가능 (예: "ㅍㄹㅅㅋ"로 "프레스카" 검색)
- **영문 발음 변환**: 영문 상표명의 한글 발음을 기반으로 검색 가능 (예: "FRESCA"의 한글 발음 "프레스카"로 검색)
- **필터링**: 등록 상태, 분류 코드, 출원일 기준 필터링 지원
- **정렬**: 다양한 필드(출원일, 등록일, 상표명 등)를 기준으로 정렬 지원
- **페이징**: 검색 결과 페이징 처리

### 자동완성 기능

- **상표명 자동완성**: 검색어 입력 시 관련 상표명 추천 (예: "프레" 입력 시 "프레스카" 추천)
- **초성 자동완성**: 초성만 입력해도 관련 상표명 추천 (예: "ㅍㄹ" 입력 시 "프레스카" 추천)
- **오타 교정**: 유사한 발음/철자의 상표명 추천 (fuzziness 기반)
- **하이라이팅**: 검색어 매칭 부분 강조 표시 (예: "<mark>프레</mark>스카")

### 상표 상세 정보

- **상세 정보 조회**: 상표 출원번호로 상세 정보 조회
- **조회수 관리**: 상표 조회 시 조회수 자동 증가 기능 (viewCount 필드)

### 기타 기능

- **데이터 로드**: JSON 파일에서 상표 데이터 로드 기능
- **시스템 상태 확인**: Elasticsearch, 인덱스, 문서 수 등 상태 확인
- **로깅**: 상세한 로그 관리 및 성능 모니터링
- **오류 처리**: 다양한 예외 상황에 대한 체계적인 오류 처리

### 기술적 특징

- **ElasticSearch 인덱스 최적화**: 검색 성능을 위한 맞춤형 매핑 및 분석기 적용
- **한글 초성 처리**: 한글 초성 추출 및 검색 최적화 (유니코드 기반)
- **영문-한글 발음 변환**: 영문 상표명의 한글 발음 변환 기능 (g2pk 라이브러리 활용)
- **n-gram 분석**: 부분 문자열 매칭 및 유사 문자열 검색 지원
- **조회수 트래킹**: 상표별 조회수 관리 기능

## 3. 기술적 의사결정에 대한 설명

### 검색 엔진 선택: Elasticsearch

상표 검색 API 구현에 있어 Elasticsearch를 선택한 주요 이유는 다음과 같습니다:

1. **JSON 기반 데이터 처리**: 상표 데이터가 JSON 형태로 제공되어 Elasticsearch의 Document 중심 구조와 완벽하게 일치합니다.

2. **텍스트 분석 기능**: 한글과 영문이 혼재된 상표명에 대해 다양한 분석기(analyzer)를 적용할 수 있어 검색 품질이 향상됩니다.

   - `nori` 분석기: 한글 형태소 분석
   - `edge_ngram`, `ngram`: 부분 문자열 매칭
   - 오타 교정 기능 (`fuzziness`)

3. **확장성**: 데이터 증가에 대비한 수평적 확장성(sharding)을 제공합니다.

4. **성능**: 역색인(inverted index) 구조로 대량 데이터에서도 빠른 검색 성능을 보장합니다.

대안으로 고려했던 접근 방식들과 비교한 결과는 다음과 같습니다:

| 접근 방식        | 장점                  | 단점                                  | 비고                                      |
| ---------------- | --------------------- | ------------------------------------- | ----------------------------------------- |
| RDBMS (MySQL 등) | 설정 간편, SQL 익숙함 | LIKE 검색 성능 저하, 텍스트 분석 한계 | 10만건 이상 데이터 시 성능 문제           |
| Redis            | 빠른 응답 속도        | 검색 기능 제한적, 메모리 부담         | 캐시용으로는 적합하나 검색엔진으로 부적합 |
| MongoDB          | JSON 저장 적합        | 텍스트 분석 기능 미흡                 | 검색 성능이 Elasticsearch보다 떨어짐      |
| Python 자체 구현 | 의존성 감소           | 메모리 부담, 느린 검색 속도           | 로직 복잡도 증가, 확장성 부족             |
| PostgreSQL + FTS | SQL + 텍스트 검색     | 한글 지원 부족                        | 한글 초성 검색 구현 어려움                |

### 검색 기능 향상: 초성 검색 및 발음 변환

1. **초성 검색 구현**:

   - 한글 특성을 고려한 사용자 경험 향상을 위해 초성 검색을 구현했습니다.
   - 색인 시점에 초성 전용 필드(productName_chosung)를 생성하여 검색 성능을 최적화했습니다.
   - 유니코드 기반 직접 구현으로 외부 라이브러리 의존성을 최소화했습니다.

2. **영문 발음 변환**:
   - 영문 상표명을 한글 발음으로 변환하여 사용자가 발음대로 검색할 수 있게 했습니다.
   - 예: "FRESCA" → "프레스카"로 변환하여 한글로 검색 가능
   - 발음 변환에는 g2pk 라이브러리를 활용했으며, 라이브러리 사용이 불가능한 환경을 위한 기본 발음 변환 로직도 구현했습니다.

### API 아키텍처: 도메인 중심 설계

1. **도메인 중심 아키텍처**:
   - 상표(trademark) 도메인을 중심으로 구조화
   - 기능별 모듈 분리 (models, schemas, services, routers)
   - 확장성을 고려한 코드 구조 설계
2. **Docker 활용 이유**:
   - Elasticsearch, Kibana 등 외부 서비스의 일관된 환경 제공
   - 개발/배포 환경 통일로 안정성 확보
   - 필요 시 수평 확장을 위한 기반 마련

### 인프라 구성: 가상환경 활용

**로컬 개발을 위한 가상환경**:

- Python venv를 통한 의존성 격리
- 개발 환경에서의 빠른 반복 개발 지원

## 4. 문제 해결 과정에서 고민했던 점

### 문제 1: 불완전한 데이터 구조에서의 검색 품질 확보

#### 문제 정의

상표 데이터를 분석했을 때, 다음과 같은 문제점이 발견되었습니다:

- `productName`이 null인 레코드가 존재함
- 한글과 영문이 혼재되어 있어 검색 난이도 증가
- 사용자 관점에서 정확한 상표명을 기억하지 못하는 경우 검색 실패 가능성 높음

#### 접근 방식

이 문제를 해결하기 위해 다음과 같은 접근법을 고려했습니다:

1. **다중 필드 검색**: `productName`과 `productNameEng` 모두에서 검색
   - 장점: 기본적인 검색 범위 확장
   - 한계: 영문과 한글 발음 불일치 문제 해결 불가
2. **단순 키워드 매칭 최적화**: 검색 알고리즘 조정만으로 해결

   - 장점: 추가 필드 없이 구현 가능
   - 한계: 초성 검색, 발음 기반 검색 구현 어려움

3. **선택한 접근법: 데이터 확장 + 복합 검색**
   - 색인 시 데이터 풍부화 (Data Enrichment): 초성 필드와 발음 변환 필드 추가
   - 복합 검색 쿼리로 다양한 검색 시나리오 처리

#### 구현 결과

```python
# 영문 상표명의 한글 발음 변환 및 초성 추출
if 'productNameEng' in data and data['productNameEng']:
    try:
        eng_pronunciation = english_to_korean_pronunciation(data['productNameEng'])
        if eng_pronunciation:
            processed_data['productNameEngPronunciation'] = eng_pronunciation

            # 발음의 초성도 추출하여 저장
            chosung = extract_chosung(eng_pronunciation)
            if chosung:
                processed_data['productNameEngPronunciation_chosung'] = chosung
    except Exception as e:
        logger.error(f"발음 변환 중 오류 발생: {eng_pronunciation}")
```

이를 통해:

1. 영문 상표명 "FRESCA"를 한글 발음 "프레스카"로 변환하여 저장
2. 변환된 발음의 초성 "ㅍㄹㅅㅋ"도 함께 저장
3. 검색 시 한글 발음으로 검색해도 영문 상표 검색 가능
4. 초성만으로도 영문 상표를 검색할 수 있는 환경 구축

#### 결과의 이점

- **데이터 불완전성 극복**: `productName`이 null이더라도 영문명을 통한 검색 가능
- **사용자 편의성 향상**: 대략적인 발음이나 초성만으로도 원하는 상표 검색 가능
- **검색 품질 향상**: 정확한 상표명을 기억하지 못해도 연관 상표 노출 확률 증가

### 문제 2: 한글 특성을 고려한 초성 검색 최적화

#### 문제 정의

한글 검색 시 초성만으로 검색하는 기능이 필요한데, 다음과 같은 기술적 과제가 존재했습니다:

- 초성 검색을 실시간으로 처리할지, 색인 시점에 처리할지 결정 필요
- 초성 추출을 위한 효율적인 방법 선택 필요
- 검색 쿼리 복잡도와 성능 간의 균형 유지 필요

#### 접근 방식 비교

1. **실시간 초성 변환 방식**:

   - 방법: 검색 쿼리 시점에 모든 데이터의 초성 변환 후 비교
   - 장점: 추가 저장 공간 불필요
   - 단점: 매 검색마다 모든 문서의 초성 변환 계산 비용 발생, 성능 저하

2. **외부 라이브러리 활용 방식**:

   - 방법: KoNLPy, Mecab 등 형태소 분석기 활용
   - 장점: 정교한 한글 처리 가능
   - 단점: 라이브러리 의존성, 모델 로딩 시간, 리소스 소모 큼

3. **선택한 접근법: 색인 시 유니코드 기반 초성 추출**:
   - 유니코드 특성을 활용한 직접 초성 추출 구현
   - 색인 시점에 전용 필드로 저장하여 검색 성능 최적화

#### 구현 결과

```python
def extract_chosung(text: str) -> Optional[str]:
    """한글 문자열에서 초성만 추출하여 반환"""
    if text is None:
        return None

    result = []

    for char in text:
        if '가' <= char <= '힣':  # 한글 문자인 경우
            # 한글 유니코드 값에서 초성 인덱스 계산
            char_code = ord(char) - ord('가')
            chosung_index = char_code // 588
            result.append(CHOSUNG_LIST[chosung_index])
        else:
            # 한글이 아닌 문자는 그대로 추가
            result.append(char)

    return ''.join(result)
```

검색 로직에서는 초성 전용 검색 패턴 적용:

```python
if chosung_only:
    query["bool"]["should"] = [
        # 한글 상표명 초성 검색
        {"match_phrase_prefix": {
            "productName_chosung": {
                "query": query_text,
                "boost": 5.0
            }
        }},
        # 영문 상표명 한글 발음 초성 검색
        {"match_phrase_prefix": {
            "productNameEngPronunciation_chosung": {
                "query": query_text,
                "boost": 4.0
            }
        }}
    ]
```

#### 결과의 이점

- **성능 최적화**: 색인 시점에 초성 추출로 검색 시 계산 비용 최소화
- **복잡도 감소**: 외부 라이브러리 없이 유니코드 기반 직접 구현으로 의존성 감소
- **사용자 경험 향상**: "ㅍㄹㅅㅋ"만 입력해도 "프레스카" 및 "FRESCA" 모두 검색 가능
- **확장성**: 코드의 복잡도를 최소화하면서도 초성 검색 기능 효율적 구현

### 문제 3: 검색 성능과 정확도 사이의 균형

#### 문제 정의

다양한 검색 기능을 제공하면서도 응답 속도를 유지해야 하는 과제가 있었습니다:

- 정확도 향상을 위한 복잡한 쿼리는 응답 시간 증가로 이어짐
- n-gram 분석은 부분 문자열 매칭에 유용하나 인덱스 크기 증가
- 초성 검색, 발음 검색, 일반 검색을 동시에 최적화해야 함

#### 접근 방식

1. **검색 쿼리 최적화**:

   - 필드별 가중치(boost) 조정으로 중요 필드 우선 순위 설정
   - 명확한 조건에 따른 쿼리 분기 처리 (초성 검색, 일반 검색 등)
   - 필수 검색(must)과 선호 검색(should) 조합으로 유연성 확보

2. **인덱스 최적화**:
   - n-gram 분석기의 최소/최대 크기 제한으로 인덱스 크기 조절
   - 자주 사용되는 필드에 대한 인덱스 최적화 (keyword, ngram 등)
   - 분석기 선택 (nori_standard, nori_search 등)으로 검색 품질 향상

#### 구현 결과

```python
# 인덱스 설정 최적화
"settings": {
    "index": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "max_ngram_diff": 9,
        "refresh_interval": "5s"
    },
    "analysis": {
        "analyzer": {
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
            # 필터 설정
            "filter": {
                "ngram_filter": {
                    "type": "ngram",
                    "min_gram": 2,
                    "max_gram": 5
                }
            }
        }
    }
}
```

검색 쿼리 최적화 구현:

```python
# 일반 검색인 경우 - should 절 구성
should_clauses = []

# 1. 한글 상표명 검색 (null이 아닌 경우)
should_clauses.append({
    "bool": {
        "must": [
            {"exists": {"field": "productName"}},
            {"multi_match": {
                "query": query_text,
                "fields": ["productName^3", "productName.ngram^2"],
                "type": "best_fields"
            }}
        ]
    }
})

# 2. 영문 상표명 검색 (null이 아닌 경우)
# 3. 영문 상표명의 한글 발음 검색
# 4. 영문 상표명의 한글 발음 초성 검색
# (생략)
```

#### 결과의 이점

- **균형된 검색 성능**: 검색 정확도와 응답 속도 사이의 최적 균형점 확보
- **사용자 경험 향상**: 다양한 검색 패턴에 모두 대응하는 유연한 시스템 구현
- **시스템 리소스 최적화**: 인덱스 크기와 메모리 사용량을 고려한 설계
- **확장성**: 향후 데이터 증가에 대비한 확장 가능한 구조 구축

## 개선하고 싶은 부분

현재 구현된 상표 검색 시스템에 대해 다음과 같은 개선 사항을 적용하고자 합니다:

### 1. 검색 성능 최적화: 캐싱 전략 도입

#### 현재 한계

현재 구현에서는 모든 검색 요청이 Elasticsearch에 직접 전달되어 처리되고 있습니다. 이는 다음과 같은 한계가 있습니다:

- 인기 검색어에 대해 반복적으로 동일한 쿼리 처리
- 피크 시간대 검색 서버 부하 집중
- 응답 시간 일관성 부족

#### 개선 방안: 가중치 기반 캐싱 시스템

인기 검색 파라미터에 대한 결과를 캐시하는 시스템을 구축하여 성능을 향상시키고자 합니다:

1. **검색 파라미터 통계 수집**:
   - 모든 검색 요청의 파라미터를 로깅하여 통계 데이터 축적
   - 파라미터별 요청 빈도, 시간대별 패턴 분석
2. **가중치 기반 캐시 관리**:

   - Redis를 활용한 캐시 레이어 구축
   - 매일 00시에 자동 배치 작업으로 인기 검색 파라미터 20개 선정
   - 선정된 파라미터에 대한 검색 결과 사전 캐싱

3. **캐시 갱신 전략**:

   - TTL(Time-To-Live) 설정으로 캐시 신선도 유지
   - 데이터 변경 시 관련 캐시 무효화 로직 구현
   - 점진적 캐시 갱신으로 성능 저하 방지

4. **Nginx 활용 Edge 캐싱**:
   - Nginx 서버에서 URI 기반 캐싱 추가 적용
   - API Gateway 레벨에서의 1차 캐시 구현

#### 기대 효과

- 인기 검색어에 대한 응답 시간 80% 이상 단축
- Elasticsearch 서버 부하 분산
- 일일 배치 작업을 통한 효율적인 캐시 관리
- 사용자 패턴에 맞춘 탄력적인 캐시 전략

### 2. 데이터 관리 이원화: RDBMS와 Elasticsearch 병행

#### 현재 한계

현재 시스템은 Elasticsearch를 유일한 데이터 저장소로 사용하고 있어 다음과 같은 제한이 있습니다:

- 데이터 수정/삭제에 대한 트랜잭션 관리 어려움
- 관계형 데이터 처리의 한계
- 백업 및 복구 프로세스 복잡성

#### 개선 방안: 데이터 관리 이원화

RDBMS와 Elasticsearch를 함께 활용하는 이원화된 데이터 관리 구조를 구축하고자 합니다:

1. **RDBMS를 마스터 데이터 소스로 활용**:
   - PostgreSQL을 주 데이터베이스로 사용
   - 상표 데이터의 CRUD 작업은 RDBMS에서 우선 처리
   - 트랜잭션 관리 및 데이터 정합성 보장
2. **데이터 동기화 메커니즘**:
   - 이벤트 기반 동기화 시스템 구축
     - RDBMS의 변경사항이 이벤트로 발행
     - Kafka 등의 메시지 큐를 통한 안정적 전달
     - Elasticsearch에서 이벤트 소비 및 인덱스 갱신
   - 동기화 상태 모니터링 및 장애 복구 프로세스 구현
3. **API 레이어 조정**:

   - 읽기 작업(검색, 조회)은 Elasticsearch 활용
   - 쓰기 작업(등록, 수정, 삭제)은 RDBMS 우선 처리
   - 트랜잭션 일관성을 위한 Two-Phase Commit 패턴 적용

4. **인덱스 재구축 최적화**:
   - 전체 재색인이 필요한 경우 RDBMS에서 데이터 추출
   - 증분 업데이트를 위한 변경 추적 필드 추가
   - 색인 버전 관리로 다운타임 없는 마이그레이션 지원

#### 기대 효과

- 데이터 관리 안정성 향상
- 검색과 트랜잭션 처리의 장점 동시 활용
- 시스템 장애 복원력 강화
- 데이터 백업 및 관리 용이성 증대
- 서비스 확장 시 유연한 대응 가능

### 3. API 요청 제한 및 DDoS 방어 전략 구현

#### 현재 한계

현재 시스템은 API 요청량에 대한 제한이 없어 다음과 같은 위험이 존재합니다:

- 과도한 요청으로 인한 서버 과부하 가능성
- DDoS 공격에 취약한 구조
- 악의적인 사용자의 시스템 자원 독점 가능성
- 정상 사용자의 서비스 이용 제한 가능성

#### 개선 방안: 다단계 요청 제한 시스템

1. **사용자/IP 기반 요청 제한**:
   - IP 주소별 요청 제한 구현 (예: 분당 60회)
   - 클라이언트 식별자(User-Agent, 세션 ID 등) 기반 추가 제한
   - Redis를 활용한 분산 환경에서의 요청 카운터 관리
2. **계층적 Rate Limiting 구현**:
   - 글로벌 레벨: 전체 API에 대한 초당 최대 요청 수 제한
   - 엔드포인트 레벨: 특정 API 엔드포인트별 요청 제한
   - 사용자 레벨: 사용자 유형에 따른 차등적 제한 적용
3. **이상 트래픽 탐지 및 차단**:
   - 패턴 기반 비정상 트래픽 탐지 알고리즘 도입
   - 급증하는 요청 패턴 감지 시 자동 제한 강화
   - CAPTCHA 등 인증 단계 추가로 봇 트래픽 필터링
4. **Nginx 및 CloudFlare 활용**:
   - Nginx rate limiting 모듈 적용 (limit_req_zone)
   - CloudFlare 등의 서비스를 활용한 DDoS 방어
   - IP 평판 데이터베이스 활용하여 악성 IP 선제적 차단

#### 기대 효과

- 시스템 안정성 및 가용성 향상
- DDoS 공격에 대한 효과적인 방어
- 공정한 리소스 분배를 통한 서비스 품질 유지
- 악의적인 사용에 대한 탐지 및 차단
- 운영 비용 최적화 및 인프라 효율성 증대
