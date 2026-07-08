# 1. Use an official, lightweight Python runtime image
FROM python:3.11-slim

# 2. Set the root working directory inside the container
WORKDIR /app

# 3. Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Install system build dependencies and clean up cache to save space
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements file first to optimize Docker layer caching
COPY requirements.txt .

# 6. Upgrade pip and install minimal required packages without local caching
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Copy your source directories into the container explicitly
COPY api/ ./api/
COPY model/ ./model/

# 8. Expose port 8000 for local reference (Render overrides this dynamically)
EXPOSE 8000

# 9. Launch the API using Render's dynamic port environment variable
# Uses 'api.api:app' to map to the api folder, api.py file, and app object
CMD ["sh", "-c", "uvicorn api.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
