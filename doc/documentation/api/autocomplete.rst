Autocomplete API
################

.. http:get:: /apy/autocomplete

   Facade for autocomplete

   If the user input ends with a "?" character, return a set of questions that may be relevant to the user.
   If there are at least 5 results from fuzzy matching, they are returned. Otherwise, results of semantic similarity
   matching are returned alongside the fuzzy matching results.

   **Example request**:

   .. sourcecode:: http

      GET /users/123/posts/web HTTP/1.1
      Host: example.com
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK

      [
          {
              "id": 1,
              "question": "What is FastAPI?",
              "answer": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.",
              "language": "en"
          },
          ...
      ]

   :query string question: User input
   :query string language: Question and results language
   :query int k: Number of results to return

   :resheader Content-Type: application/json
   :statuscode 200: List of matching questions