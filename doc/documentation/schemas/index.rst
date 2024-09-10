Schemas
=======

A schema represent the **structure of the data** that is exchanged between the client and the server.

In this project, we use `Pydantic <https://docs.pydantic.dev/latest/>`__ to define the schemas. Pydantic is a data validation and parsing library that uses Python type annotations to define the schema of the data, it is also used to serialize and deserialize data to and from JSON.

.. note::
    Usually, this are known as Pydantic **model**. However, as this project implements SQLAlchemy for data management, we want to avoid confusion between SQLAlchemy ORM models, which represent the structure of the database tables, and the Pydantic models. This lead us to chose an alternative naming (recommended in FastAPI documentation).

Database schemas
----------------

We grouped in modules the schemas that are related to a same table. In each module, we can find schemas that have similar use cases for their respective entity.

- Base schema
    Base object from which all other schemas inherit. This is also the one used in case of relation between schemas.
- Create schema
    To create a new entry in the database table. Usually, there is a second one for creation of multiple entries.
- Update schema
    To update an existing entry in the database table.
- Schema named after its entity
    Represents the object that will be returned to the user through the API.

Other schemas
-------------

Below, we have schemas that are not directly related to the database tables, but are used in the API.

.. automodule:: schemas.common
    :members:
    :inherited-members: BaseModel

.. toctree::
   :hidden:

   document
   question
   source