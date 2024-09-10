Indexing config
===============

The **indexing** config has a single parameter which is ``auto_init``.
If set to ``true``, the app will automatically index data from the .csv files stored in ``indexing/data/``.

CSV Files in ``indexing/data/RAG/`` directory are indexed as RAG documents and files in ``indexing/data/FAQ/`` directory are indexed as FAQ data.

Its **enabled** parameter is always set to ``true``.

In ``config.yaml``, if **indexing** is set to ``true``, then **auto_init** is set to ``true``.
By default, **auto_init** is set to ``false``.

The two following example configurations are equivalent:

.. code-block:: yaml

    indexing: true

.. code-block:: yaml

    indexing:
      auto_init: true

**Indexing* configuration also has an embedding model as parameter. **Embedding** takes as value the name of the model to use for the embedding process, the list of supported models can be found in ``config/ai_models/supported.py``.

.. automodule:: config.indexing.config
    :members: