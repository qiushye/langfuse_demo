FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LANGCHAIN_TRACING_V2=false \
    LANGSMITH_TRACING=false \
    PORT=8000

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Provide sane defaults; override via k8s env
ENV MODEL_TYPE=deepseek \
    MODEL_NAME=deepseek-chat \
    ENABLE_INTENT_CLASSIFICATION=true \
    LANGFUSE_TIMEOUT=20

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

