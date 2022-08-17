FROM quay.io/centos/centos:stream8

RUN dnf -y module install python39 && dnf -y install python39 python39-pip 
RUN curl -s https://packagecloud.io/install/repositories/akopytov/sysbench/script.rpm.sh | bash
RUN dnf -y install sysbench
RUN mkdir /app
ADD sysbench_plugin.py /app
ADD test_sysbench_plugin.py /app
ADD requirements.txt /app
ADD tests /app/tests/
ADD configs /app/configs/
WORKDIR /app

RUN pip3 install -r requirements.txt
RUN python3.9 test_sysbench_plugin.py

ENTRYPOINT ["python3.9", "/app/sysbench_plugin.py"]
CMD []

LABEL org.opencontainers.image.title="Sysbench Arcalot Plugin"
LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugins/python/sysbench/blob/main/sysbench_plugin.py"
LABEL org.opencontainers.image.licenses="Apache-2.0+GPL-2.0-only"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL io.github.arcalot.arcaflow.plugin.version="1" 