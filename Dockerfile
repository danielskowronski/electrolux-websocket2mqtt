FROM python:3.14-slim
LABEL org.opencontainers.image.source=https://github.com/danielskowronski/electrolux-websocket2mqtt
RUN python -m pip install hatch
RUN mkdir -p /app/
WORKDIR /app
COPY pyproject.toml /app

RUN hatch dep show requirements > /app/requirements.txt && \
  python -m pip install -r /app/requirements.txt

COPY ./src/electrolux_websocket2mqtt /app/src/electrolux_websocket2mqtt
COPY ./tests /app/tests
COPY ./README.md /app/README.md
RUN python -m pip install -e .

CMD ["electrolux-websocket2mqtt"]
