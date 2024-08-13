import os
import pytest
from testcontainers.postgres import PostgresContainer

from database.database import get_db
from schemas.source import Source

postgres = PostgresContainer("ankane/pgvector")


@pytest.fixture(scope="module", autouse=True)
def setup(request):
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


def test_get_or_create_no_data():
    """
    Test get_or_create method with no data in the database
    Create a source.
    :return: none
    """
    from database.database import get_db
    from database.service.source import source_service
    db = get_db()
    new_source = source_service.get_or_create(db, Source(id=0, url="https://www.test.ch"))

    assert new_source.url == "https://www.test.ch"
    assert new_source.id == 0
    assert source_service.get_by_url(db, "https://www.test.ch") == new_source
