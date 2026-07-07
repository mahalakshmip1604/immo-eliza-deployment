# 1. Use an official, lightweight Python runtime image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Install system dependencies and clean up cache in one step to save space
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy only the requirements file first to utilize Docker build caching
COPY requirements.txt .

# 6. Upgrade pip and install Python packages without keeping a local cache
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of your application code into the container
COPY . .

# 8. Expose the port FastAPI will run on
EXPOSE 8000

# 9. Run the application bound to 0.0.0.0 so external networks can access it
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
