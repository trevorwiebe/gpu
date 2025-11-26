FROM nvidia/cuda:12.1.0-devel-ubuntu20.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Upgrade pip
RUN pip install --upgrade pip

# Install PyTorch with CUDA support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install vLLM and dependencies
RUN pip install \
    vllm \
    websockets \
    transformers \
    accelerate

# Create working directory
WORKDIR /app

# Copy the node service script
COPY node/src/node_service.py /app/

# Environment variables (can be overridden at runtime)
ENV HUB_URL=ws://host.docker.internal:8000/ws
ENV NODE_ID=node_docker_1
ENV MODEL_PATH=/models/llama-3.1-8b

# Expose port (not really needed for client, but good practice)
EXPOSE 8080

# Run the node service
CMD ["python", "node_service.py"]