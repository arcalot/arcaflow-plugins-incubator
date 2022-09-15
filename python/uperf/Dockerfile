FROM quay.io/cloud-bulldozer/uperf AS tester

FROM quay.io/centos/centos:stream8
RUN dnf module -y install python39 && dnf install -y python39 python39-pip lksctp-tools-devel
COPY --from=tester /usr/bin/uperf /uperf/uperf
RUN mkdir /plugin
ADD uperf_plugin.py /plugin
ADD uperf_schema.py /plugin
ADD test_uperf_plugin.py /plugin
ADD requirements.txt /plugin
WORKDIR /plugin

RUN pip3 install -r requirements.txt
RUN python3.9 test_uperf_plugin.py
RUN rm -f /uperf/uperf

EXPOSE 20000

ENTRYPOINT ["python3.9", "uperf_plugin.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugins/blob/main/python/uperf/Dockerfile"
LABEL org.opencontainers.image.licenses="Apache-2.0+GPL-3.0-only"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Uperf Arcalot Plugin"
LABEL io.github.arcalot.arcaflow.plugin.version="1"