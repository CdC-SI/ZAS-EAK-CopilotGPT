RAG configuration
=================

The **RAG** service is enabled by default and can be disabled by setting ``rag`` to ``false``.
Otherwise, the following parameters can be set:

- **stream**: if set to ``true``, the app will stream the RAG output to the client as it is generated.
- **LLM**: configuration for the Language Model

  - *model*: the name of the model to use for the Language Model, the list of supported models can be found in ``config/ai_models/supported.py``.
  - *temperature*: the temperature to use for the Language Model
  - *max_tokens*: the maximum number of tokens to generate
  - *top_p*: the top_p value to use for the Language Model

- **Retrieval**: configuration for the retrieval process

  - *top_k*: the number of documents to retrieve
  - *metric*: the metric to use for similarity calculation. The possible values are

    - ``cosine_similarity``
    - ``l1_distance``
    - ``l2_distance``
    - ``negative_inner_product``

  - *retrievers*: a list of retrievers or string to use for the retrieval process.

    - *top_k*: the number of documents to retrieve
    - *query_rewriting*: configuration for the query rewriting retriever
    - *top_k*: the number of documents to retrieve
    - *n_alt_queries*: the number of alternative queries to generate

  - *Reranking*: configuration for the reranking process, if set to ``false``, the reranking process will be disabled. By default, the reranking process is enabled.

    - *model*: the name of the model to use for the reranking process, the list of supported models can be found in ``config/ai_models/supported.py``.
    - *top_k*: the number of documents to rerank

The list of available retrievers can be found in ``config/rag/retrievers.py``.
Following are some possible *retrievers* configurations:

.. code-block:: yaml

    rag:
      Retrieval:
        retrievers:
        - top_k:
          top_k: 100
        - query_rewriting:
          top_k: 10
          n_alt_queries: 5

.. code-block:: yaml

    rag:
      Retrieval:
        retrievers:
        - top_k
        - query_rewriting

.. code-block:: yaml

    rag:
      Retrieval:
        retrievers:
        - top_k:
          top_k: 100
        - query_rewriting

.. automodule:: config.rag.config
    :members:

.. automodule:: config.rag.retrieval
    :members:

Retrievers
----------

.. automodule:: config.rag.retrievers
    :members:
