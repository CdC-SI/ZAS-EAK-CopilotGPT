# Use the official Python image as the base
FROM python:3.9-slim

WORKDIR /app

# Install build-essential and cmake
RUN apt-get update && \
    apt-get install -y build-essential cmake && \
    apt-get clean

# Copy the requirements into the container and install them
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the code into the container
COPY . .

# Set pythonpath
ENV PYTHONPATH="/app:/app/config"

# Standard command that is executed when the container is started
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
