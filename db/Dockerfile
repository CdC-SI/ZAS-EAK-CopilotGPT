FROM postgres:latest

# Fügen von benutzerdefinierten Konfigurationsdateien hinzu, falls erforderlich
COPY ./custom_postgres.conf /etc/postgresql/postgresql.conf

# Fügen von Datenbankinitialisierungsskripten hinzu, falls erforderlich
COPY ./init.sql /docker-entrypoint-initdb.d/

# Optional: Definiere zusätzliche Konfigurationen hier
ENV POSTGRES_LOG_STATEMENT=all

EXPOSE 5432
