FROM python:3.14-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps build-base \
    && pip install --no-compile --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY skimbot.py .

CMD ["python", "skimbot.py"]
