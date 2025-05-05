# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Set environment variables (optional, overridden by .env if using docker-compose)
ENV PYTHONUNBUFFERED=1

# Default command: run the Prefect ETL flow
CMD ["python", "prefect_flow.py"]
