#!/bin/bash
set -e

# Wait for PostgreSQL to start
sleep 5

# Create the table
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
CREATE TABLE IF NOT EXISTS data (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    language VARCHAR(2) DEFAULT 'de'
);
EOSQL

# Load data from CSV
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
\COPY data(url, created_at, modified_at, question, answer, language) FROM '/docker-entrypoint-initdb.d/data.csv' DELIMITER ',' CSV HEADER;
EOSQL