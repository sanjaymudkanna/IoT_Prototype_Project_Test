# Example: Running the application with Docker (optional)

FROM python:3.11-slim

# Install system dependencies for serial and I2C
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    i2c-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config.yaml .

# Create logs directory
RUN mkdir -p logs

# Run the application
CMD ["python", "src/main.py"]
