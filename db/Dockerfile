FROM ankane/pgvector

# Copy custom configuration file
COPY ./custom_postgres.conf /etc/postgresql/postgresql.conf

# Add database initialisation scripts if required
COPY ./init.sql /docker-entrypoint-initdb.d/

# Optional: Define additional configurations here
ENV POSTGRES_LOG_STATEMENT=all

EXPOSE 5432
