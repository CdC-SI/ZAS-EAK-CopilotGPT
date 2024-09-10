Autocomplete config
===================

The **autocomplete** feature is enabled by default and can be disabled by setting ``autocomplete`` to ``false``.
Otherwise, the following parameters can be set:

* **limit**: the maximum number of results to return
* **exact_match**: configuration for exact matching

  * *limit*: the maximum number of exact matches to return

* **levenshtein_match**: configuration for Levenshtein matching

  * *limit*: the maximum number of Levenshtein matches to return
  * *threshold*: the minimum similarity threshold for a match, a positive integer

* **semantic_match**: configuration for semantic matching

  * *limit*: the maximum number of semantic matches to return
  * *metric*: the metric to use for similarity calculation. The possible values are

    * ``cosine_similarity``
    * ``l1_distance``
    * ``l2_distance``
    * ``negative_inner_product``

* **trigram_match**: configuration for trigram matching

  * *limit*: the maximum number of trigram matches to return
  * *threshold*: the minimum similarity threshold for a match, between 0 and 1

**Limits** must be positive integers.

.. automodule:: config.autocomplete.config
    :members:

.. automodule:: config.autocomplete.matching
    :members:
