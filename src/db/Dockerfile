FROM ankane/pgvector

# Copy custom configuration file
COPY ./custom_postgres.conf /etc/postgresql/postgresql.conf

# Add database initialisation scripts if required
COPY ./init.sql /docker-entrypoint-initdb.d/

# Copy the initialization script
COPY init-db.sh /docker-entrypoint-initdb.d/init-db.sh
COPY all_faq_data.csv /docker-entrypoint-initdb.d/data.csv

# Make the script executable
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

# Optional: Define additional configurations here
ENV POSTGRES_LOG_STATEMENT=all

EXPOSE 5432
