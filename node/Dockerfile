FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CUDA_VISIBLE_DEVICES=0

# Install system dependencies and set up Python
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    curl \
    openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu128

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt huggingface_hub

# Create sshd run directory (required by sshd)
RUN mkdir /var/run/sshd

# Create models directory (models will be downloaded dynamically)
RUN mkdir -p /models

# Create app directory
WORKDIR /app

# Copy application code
COPY *.py .
COPY models/ ./models/
COPY routers/ ./routers/

# Expose port
EXPOSE 22 8005

# Run the application
RUN echo 'export PUBLIC_IPADDR=localhost' > /app/.env.sh && \
    echo 'export EXTERNAL_PORT=8001' >> /app/.env.sh && \
    echo 'export ROUTER_PUBLIC_IPADDR=localhost:5173' >> /app/.env.sh
CMD ["bash", "-c", "source /app/.env.sh && /usr/sbin/sshd && uvicorn app:app --host 0.0.0.0 --port 8005"]