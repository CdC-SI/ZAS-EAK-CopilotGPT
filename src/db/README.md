# Migrations

1. First create a migration file under the db migrations directory, eg:
```
src/db/migrationsV1__alter_chat_feedback_fk.sql
```

2. Then, modify the db service in docker-compose.yml to mount the migrations directory under volumes:

```
volumes:
    - ./src/db/data:/var/lib/postgresql/data
    - ./src/db/migrations:/docker-entrypoint-initdb.d/migrations
```

3. Then restart the db container to apply the changes:
```
docker-compose down db
docker-compose up -d db
```

4. Then execute the migration:
```
docker-compose exec db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /docker-entrypoint-initdb.d/migrations/V1__alter_chat_feedback_fk.sql
```

Note: Replace `${POSTGRES_USER}` and `${POSTGRES_DB}` with actual values from your `.env` file.
