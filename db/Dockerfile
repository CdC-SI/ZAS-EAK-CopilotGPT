FROM ankane/pgvector

# Copy custom configuration file
COPY ./custom_postgres.conf /etc/postgresql/postgresql.conf

# Fügen von Datenbankinitialisierungsskripten hinzu, falls erforderlich
COPY ./init.sql /docker-entrypoint-initdb.d/

# Optional: Definiere zusätzliche Konfigurationen hier
ENV POSTGRES_LOG_STATEMENT=all

EXPOSE 5432
