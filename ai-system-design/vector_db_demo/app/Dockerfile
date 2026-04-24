FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=1000 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install \
    fastapi==0.115.0 \
    uvicorn[standard]==0.30.6 \
    qdrant-client==1.11.1 \
    pydantic==2.9.2 \
    --retries 20 \
    --timeout 1000

RUN pip install \
    torch \
    --index-url https://download.pytorch.org/whl/cpu \
    --retries 20 \
    --timeout 1000

RUN pip install \
    sentence-transformers==3.0.1 \
    --retries 20 \
    --timeout 1000

COPY main.py .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]