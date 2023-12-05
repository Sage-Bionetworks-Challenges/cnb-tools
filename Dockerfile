FROM python:3.12-alpine 

WORKDIR /root/cnb-tools

COPY ./ ./
RUN pip install --upgrade pip && \
    pip install .

ENTRYPOINT [ "cnb-tools" ]
