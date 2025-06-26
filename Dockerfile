FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-compile --no-cache-dir -r requirements.txt

COPY skimbot.py .

CMD ["python", "skimbot.py"]
