FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

WORKDIR /app

RUN pip install --no-cache-dir poetry==$POETRY_VERSION

COPY pyproject.toml poetry.lock* README.md ./
COPY docforge ./docforge
COPY tests ./tests

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "docforge.main:app", "--host", "0.0.0.0", "--port", "8000"]
