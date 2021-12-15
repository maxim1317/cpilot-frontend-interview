FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /home/server

COPY app.py .

ENV MODULE_NAME=api
ENV APP_MODULE=api:app
ENV WORKERS_PER_CORE=1

ENV MIN_DEVICES=3
ENV MAX_DEVICES=7

ENV FASTAPI_PORT=8000

CMD uvicorn app:app \
    --host 0.0.0.0 \
    --port ${FASTAPI_PORT} \
    --workers ${WORKERS_PER_CORE}
