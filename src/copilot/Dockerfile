# Use the official Python image as the base
FROM python:3.10-slim

# Comment bellow for use on ZAS network
RUN apt-get update && apt-get install -y git

# Uncomment bellow for use on ZAS network
# RUN apt-get update && \
#    apt-get install -y git && \
#    apt-get clean && \
#    git config --global http.proxy "$HTTP_PROXY" && \
#    git config --global https.proxy "$HTTPS_PROXY"

WORKDIR /app

# Copy the requirements into the container and install them
# Comment bellow for use on ZAS network
COPY requirements.txt .
RUN pip install -r requirements.txt
# Uncomment bellow for use on ZAS network
# RUN pip install   \
#    --trusted-host pypi.org  \
#    --trusted-host pypi.python.org  \
#    --trusted-host files.pythonhosted.org  \
#    -r requirements.txt

# Copy the rest of the code into the container
COPY . .


ENV PYTHONPATH="/app:/app/app:/app/config"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]