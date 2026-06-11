FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /root/cnb-tools

COPY ./ ./
RUN uv pip install --system .

ENTRYPOINT [ "cnb-tools" ]
CMD [ "--help" ]
