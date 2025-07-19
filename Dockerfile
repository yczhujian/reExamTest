FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code
COPY api/ ./api/

# Set environment variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8000

# Change to api directory
WORKDIR /app/api

# Start the application
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}