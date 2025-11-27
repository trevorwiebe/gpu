FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/models/HuggingFaceTB/SmolLM2-135M-Instruct

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install huggingface-cli
RUN pip install huggingface_hub

# Create models directory
RUN mkdir -p /models/HuggingFaceTB/SmolLM2-135M-Instruct

# Download SmolLM2-135M-Instruct model
RUN huggingface-cli download HuggingFaceTB/SmolLM2-135M-Instruct --local-dir /models/HuggingFaceTB/SmolLM2-135M-Instruct

# Create app directory
WORKDIR /app

# Copy application code
COPY app.py .

# Expose port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8005"]