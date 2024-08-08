FROM ankane/pgvector

# Copy custom configuration file
COPY ./custom_postgres.conf /etc/postgresql/postgresql.conf

# Optional: Define additional configurations here
ENV POSTGRES_LOG_STATEMENT=all

EXPOSE 5432
