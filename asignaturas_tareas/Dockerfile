
# Etapa de construcción
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Etapa de ejecución
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/

RUN useradd -m -u 10001 appuser

USER 10001

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
