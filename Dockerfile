FROM python:3.12-slim

WORKDIR /root/cnb-tools

COPY ./ ./
RUN pip install --upgrade pip && \
    pip install .

ENTRYPOINT [ "cnb-tools" ]
CMD [ "--help" ]
