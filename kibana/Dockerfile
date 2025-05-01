FROM docker.elastic.co/kibana/kibana:7.17.0

# Kibana 설정 파일 복사
COPY kibana.yml /usr/share/kibana/config/

# 권한 조정
USER root
RUN chown -R kibana:kibana /usr/share/kibana/config/
USER kibana