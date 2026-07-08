FROM python:3.11-slim
WORKDIR /app
ENV PYTHONTONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY model/ ./model/

EXPOSE 8000

# This line fixes the error by pointing to api/api.py
CMD ["sh", "-c", "uvicorn api.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
