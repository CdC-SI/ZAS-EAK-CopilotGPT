Database
########

The database and connection to it is managed by the :mod:`database` module. The database is a PostgreSQL database and its structure is defined in the :mod:`database.models` module.

At the start of the app, :meth:`database.database.get_engine()` is called to instantiate an engine and a sessionmaker.

Engine
    Create and manage connections to the database

Sessionmaker
    Create a session object which is used to interact with the database.

Every time a request is made to the server, a new session is created through :meth:`database.database.get_db()` and used to interact with the database. After the request is finished, the session is closed.

.. automodule:: database.database
   :members:

.. toctree::
   :hidden:

   tables
   services/index
