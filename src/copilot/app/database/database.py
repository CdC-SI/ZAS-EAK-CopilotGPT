from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from . import models

from config.db_config import DB_PARAMS

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['database']}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
with engine.connect() as con:
    con.execute(text("""
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
    """))
    con.commit()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
