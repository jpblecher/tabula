FROM python:3.12.3

# Install Java
RUN apt-get update && apt-get install -y --no-install-recommends default-jre \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    python-multipart \
    tabula-py \
    pandas

# Copy application code
COPY app.py .

# Same port pattern as your Whisper app
EXPOSE 8000

# Same uvicorn structure
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
