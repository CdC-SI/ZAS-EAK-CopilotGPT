#!/bin/sh

echo "Checking if langfuse schema exists..."
psql $DATABASE_URL -c "CREATE SCHEMA IF NOT EXISTS langfuse;"
