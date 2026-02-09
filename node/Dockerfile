FROM vastai/pytorch:2.10.0-cuda-12.8.1-py310-24.04

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install application dependencies into the base image's venv
COPY requirements.txt .
RUN /venv/main/bin/pip install --no-cache-dir -r requirements.txt

# Create models directory (models downloaded dynamically)
RUN mkdir -p /models

WORKDIR /app

COPY *.py .
COPY models/ ./models/
COPY routers/ ./routers/

EXPOSE 8005

# Add uvicorn as a supervisor-managed service (base image uses supervisor)
RUN printf '[program:uvicorn]\ncommand=/venv/main/bin/uvicorn app:app --host 0.0.0.0 --port 8005\ndirectory=/app\nautostart=true\nautorestart=true\nstdout_logfile=/dev/stdout\nstdout_logfile_maxbytes=0\nstderr_logfile=/dev/stderr\nstderr_logfile_maxbytes=0\n' > /etc/supervisor/conf.d/uvicorn.conf
