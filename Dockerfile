FROM python:3.12-slim

ENV PYTHONPATH=/app:$PYTHONPATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc libpq-dev python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

CMD ["python", "src/app/main.py"]