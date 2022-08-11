FROM quay.io/centos/centos:stream8

RUN dnf module -y install python39 && dnf install -y python39 python39-pip && dnf -y install git stress-ng

RUN mkdir /plugin
RUN chmod 777 /plugin
ADD stressng_plugin.py /plugin
#ADD test_smallfile_plugin.py /plugin
ADD requirements.txt /plugin
ADD stressng_example.yaml /plugin
ADD LICENSE /plugin
RUN chmod +x /plugin/stressng_plugin.py 
WORKDIR /plugin

RUN pip3 install -r requirements.txt

USER 1000

ENTRYPOINT ["/plugin/stressng_plugin.py -f stressng_example.yaml"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/mkarg75/arca-stressng"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Arcaflow stress-ng workload plugin"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
LABEL io.github.arcalot.arcaflow.plugin.privileged="0"
LABEL io.github.arcalot.arcaflow.plugin.hostnetwork="0"
