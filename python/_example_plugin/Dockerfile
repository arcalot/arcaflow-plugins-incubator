FROM quay.io/centos/centos:stream8

RUN dnf module -y install python39 && dnf install -y python39 python39-pip

RUN mkdir /plugin
ADD example_plugin.py /plugin
ADD test_example_plugin.py /plugin
ADD requirements.txt /plugin
ADD https://raw.githubusercontent.com/arcalot/arcaflow-plugins/main/LICENSE /plugin
RUN chmod +x /plugin/example_plugin.py /plugin/test_example_plugin.py
WORKDIR /plugin

RUN pip3 install -r requirements.txt
RUN /plugin/test_example_plugin.py

USER 1000

ENTRYPOINT ["/plugin/example_plugin.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugins/tree/main/python/_example_plugin"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Hello world!"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
