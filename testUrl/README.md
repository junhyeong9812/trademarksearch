# 상표 검색 API 테스트 URL 모음

## 기본 검색 테스트 URL

1. **일반 키워드 검색**

```
http://localhost:8000/api/trademarks/?query=프레스카
```

2. **상태별 필터링**

```
http://localhost:8000/api/trademarks/?status=등록
```

3. **상품 분류 코드 기반 검색**

```
http://localhost:8000/api/trademarks/?main_code=30
```

4. **유사군 코드 기반 검색**

```
http://localhost:8000/api/trademarks/?sub_code=G0301
```

5. **날짜 범위 검색**

```
http://localhost:8000/api/trademarks/?start_date=1995-01-01&end_date=1997-12-31
```

## 복합 검색 테스트 URL

6. **키워드 + 상태 + 코드 조합**

```
http://localhost:8000/api/trademarks/?query=프레스카&status=등록&main_code=30
```

7. **페이징 처리 테스트**

```
http://localhost:8000/api/trademarks/?query=프레스카&page=1&size=20
```

8. **정렬 기능 테스트**

```
http://localhost:8000/api/trademarks/?query=프레스카&sort_field=applicationDate&sort_order=desc
```

9. **다중 정렬 필드 테스트**

```
http://localhost:8000/api/trademarks/?query=프레스카&sort_field=applicationDate,productName&sort_order=desc,asc
```

## 초성 검색 테스트 URL

10. **한글 초성 검색**

```
http://localhost:8000/api/trademarks/?query=ㅍㄹㅅㅋ
```

11. **영문 발음 초성 검색**

```
http://localhost:8000/api/trademarks/?query=ㅍㄹㅅㅋ&main_code=30
```

## 자동완성 테스트 URL

12. **기본 자동완성**

```
http://localhost:8000/api/trademarks/autocomplete?query=프레
```

13. **자동완성 결과 수 제한**

```
http://localhost:8000/api/trademarks/autocomplete?query=프&size=5
```

14. **초성 기반 자동완성**

```
http://localhost:8000/api/trademarks/autocomplete?query=ㅍㄹ
```

## 상세 조회 테스트 URL

15. **상표 상세 정보 조회**

```
http://localhost:8000/api/trademarks/4019950043843
```

16. **조회수 증가 없이 상세 정보 조회**

```
http://localhost:8000/api/trademarks/4019950043843?increment_count=false
```

## 시스템 상태 확인 URL

17. **API 상태 확인**

```
http://localhost:8000/api/trademarks/status
```

18. **시스템 헬스 체크**

```
http://localhost:8000/health
```

## 데이터 관리 URL

19. **데이터 수동 로드**

```
http://localhost:8000/api/trademarks/load-data?file_path=data/trademark_sample.json
```

## 사용 방법

위 URL들을 다음과 같은 방법으로 테스트할 수 있습니다:

1. 웹 브라우저에서 직접 URL 입력
2. Postman, Insomnia 등의 API 테스트 도구 사용
3. curl 명령어로 터미널에서 테스트:
   ```bash
   curl "http://localhost:8000/api/trademarks/?query=프레스카"
   ```
4. Swagger UI를 통한 테스트:
   ```
   http://localhost:8000/docs
   ```
