from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker, Session

from . import models
from config.db_config import DBCONFIG

import time

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_db():
    """
    Get a database connection

    Returns
    -------
    Session
    """
    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Function to check if db is up
def get_engine(retries: int = 10, delay: int = 5):
    """
    Get an engine object that manages connection to the database

    Parameters
    ----------
    retries : int
        Number of retries before giving up on connecting to the database
    delay : int
        Delay between each retries

    Returns
    -------
    Engine
    """
    attempt = 0
    while attempt < retries:
        try:
            engine = create_engine(DBCONFIG.url, future=True, echo=DBCONFIG.echo)

            # Try to connect to check if the connection is established
            connection = engine.connect()
            connection.close()
            print("Database connection established.")
            return engine

        except Exception:
            attempt += 1
            print(f"Attempt {attempt} failed: Database is not ready. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Failed to connect to the database after multiple attempts.")


if DBCONFIG.enabled:
    logger.info("Connecting to database...")
    logger.info(DBCONFIG)

    engine = get_engine()
    with engine.connect() as con:
        con.execute(text("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """))
        con.commit()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    models.Base.metadata.create_all(bind=engine)
else:
    logger.info("Running without database.")