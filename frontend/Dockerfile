# Verwende das offizielle Python-Image als Basis
FROM python:3.11-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Anforderungen in den Container und installiere sie
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Kopiere den Rest des Codes in den Container
COPY . .

EXPOSE 8501

RUN apt-get update && apt-get install -y curl
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "home.py", "--server.port=8501", "--server.address=0.0.0.0"]