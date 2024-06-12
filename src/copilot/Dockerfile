# Use the official Python image as the base
FROM python:3.9-slim

# Copy the requirements into the container and install them
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the code into the container
COPY copilot .

# Set pythonpath
ENV PYTHONPATH="/app:/app/config"

# Standardbefehl, der ausgeführt wird, wenn der Container gestartet wird
CMD ["uvicorn", "copilot.main:app", "--host", "0.0.0.0", "--port", "8011"]
