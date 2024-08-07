API
###

The ``main.py`` file sets up a FastAPI application *(/apy)* with multiple sub-applications. Each sub-application provide services from one of the main functionalities of the EAK/ZAS CopilotGPT.

Autocomplete *(/apy/autocomplete)*
    Provides an endpoint for questions autocomplete suggestions when typing a message in the search bar.

Indexing *(/api/indexing)*
    Provides an endpoint for indexing new documents into the database that can be used by the autocomplete or the RAG functionalities.

RAG *(/api/rag)*
    Provides an endpoint for the RAG (Retrieval-Augmented Generation) model to generate responses to user queries based on the indexed documents.

Beside, ``main.py`` sets up CORS (Cross-Origin Resource Sharing) middleware to allow the frontend to access the API, a lifespan context manager that initializes the databases with some example data, and a dummy endpoint to check if the API is running.

.. automodule:: main
   :members:

.. toctree::
   :hidden:

   autocomplete
   indexing
   rag