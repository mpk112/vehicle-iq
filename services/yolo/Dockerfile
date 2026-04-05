FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and YOLO
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Download YOLOv8n model on build (caching for faster startup)
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Expose port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8002"]
