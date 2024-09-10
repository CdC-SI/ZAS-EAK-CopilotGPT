Configuration
=============

The configuration of the app is loaded from the file `config.yaml` stored in the `config` directory.
It is loaded at the start of the app then dispatched and stored in dataclasses.

Database configuration is loaded from .env file and also stored in a dataclass.

Below, is an example configuration file containing all the possible configuration options:

.. code-block:: yaml

    autocomplete:
      limit: 15
      exact_match:
        limit: 10
      levenshtein_match:
        limit: 10
        threshold: 50
      semantic_match:
        limit: 10
        metric: cosine_similarity
      trigram_match:
        limit: 10
        threshold: 0.4

    indexing: true

    rag:
      LLM:
        model: gpt-4o-mini
        temperature: 0
        max_tokens: 2048
        top_p: 0.95
      Retrieval:
        metric: cosine_similarity
        retrievers:
        - top_k:
          top_k: 100
        - query_rewriting:
          top_k: 10
          n_alt_queries: 5
        top_k: 100
        top_k: 10
        Reranking:
          model: rerank-multilingual-v3.0
          top_k: 5
      enabled: true
      stream: true

All parameters are optional and have default values, meaning that the app can run without a configuration file.
A possible more minimal configuration file could look like this:

.. code-block:: yaml

    autocomplete: false
    indexing: false
    rag: true

By default, autocomplete and indexing are enabled, while RAG is disabled.

.. toctree::
   :hidden:

   clients
   database
   services/index
