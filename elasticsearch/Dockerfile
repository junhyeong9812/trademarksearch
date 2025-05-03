FROM docker.elastic.co/elasticsearch/elasticsearch:7.17.0

# Nori 한국어 분석기 플러그인 설치
RUN bin/elasticsearch-plugin install analysis-nori

# Elasticsearch 설정 파일 복사
COPY elasticsearch.yml /usr/share/elasticsearch/config/

# 동의어 사전 파일 복사
COPY synonym.txt /usr/share/elasticsearch/config/analysis/synonym.txt

# 권한 조정
USER root
RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config/
USER elasticsearch