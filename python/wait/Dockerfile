FROM quay.io/centos/centos:stream8

RUN dnf module -y install python39 && dnf install -y python39 python39-pip

RUN mkdir /plugin
ADD wait_plugin.py /plugin
ADD test_wait_plugin.py /plugin
ADD requirements.txt /plugin
WORKDIR /plugin

RUN pip3.9 install -r requirements.txt
RUN python3.9 test_wait_plugin.py

ENTRYPOINT ["python3.9", "wait_plugin.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugins/blob/main/python/wait/Dockerfile"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Arcalot Wait Plugin"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
