FROM python:3.11-slim

WORKDIR /app

#Install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


#Copy your API code and trained model
COPY api/ ./api/
COPY models/ ./models/

WORKDIR /app/api

#Render sets $PORT dynamically — don't hardcode 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]