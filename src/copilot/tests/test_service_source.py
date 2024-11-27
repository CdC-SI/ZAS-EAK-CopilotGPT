import os
import pytest
from testcontainers.postgres import PostgresContainer

from sqlalchemy import text
from sqlalchemy.orm import Session

from config.db_config import DBConfiguration

postgres = PostgresContainer("ankane/pgvector")


@pytest.fixture(scope="session")
def engine(request):
    postgres.start()

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)
    os.environ["DB_CONN"] = postgres.get_connection_url()
    os.environ["POSTGRES_HOST"] = postgres.get_container_host_ip()
    os.environ["POSTGRES_PORT"] = postgres.get_exposed_port(5432)
    os.environ["POSTGRES_USER"] = postgres.username
    os.environ["POSTGRES_PASSWORD"] = postgres.password
    os.environ["POSTGRES_DB"] = postgres.dbname

    os.environ["RUN_WITHOUT_DB"] = "true"

    from database.database import get_engine

    return get_engine(DBConfiguration())


@pytest.fixture(scope="session")
def tables(engine):
    from database.models import Base

    with engine.connect() as con:
        con.execute(
            text(
                """
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """
            )
        )
        con.commit()

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def dbsession(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


def test_source_0(dbsession):
    """
    Test get_or_create method with no data in the database
    Create a source.
    :return: none
    """
    from database.service.source import source_service
    from schemas.source import SourceCreate

    new_source = source_service.get_or_create(
        dbsession, SourceCreate(url="https://www.test.ch")
    )

    assert new_source.url == "https://www.test.ch"
    assert new_source.id == 1
    assert (
        source_service.get_by_url(dbsession, "https://www.test.ch")
        == new_source
    )
