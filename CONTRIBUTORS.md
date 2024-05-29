## Open-Source Collaboration Best Practices
Please refer yourself to the [best practices document](https://cdc-si.github.io/eak-copilot/guidelines/opensource.html) for guidelines on how to contribute to this project.

## Issue Template

Please use the following template to submit an issue:

```
**Issue Title**

Setup /get_docs endpoint in backend with FastAPI.

**Description**

Setup a document retrieval endpoint in backend.

Do a semantic similarity match (cosine similarity) on indexed documents in postgres vector DB.

Takes as input a user query such as: {"query": query} and returns a response such as {"contextDocs": docs, "sourceUrl": url}.

Will be called from the frontend when a user inputs a query that doesn't match an autocomplete suggestion.

**Steps to Reproduce**

For a feature, skip this step. For a bug, detail the steps to reproduce the bug.

    Go to '...'
    Click on '....'
    Scroll down to '....'
    See error

**Expected Behavior**

For a feature, skip this step. For a bug, describe what you expected to happen when following the steps above.

**Actual Behavior**

For a feature, skip this step. For a bug, describe what actually happened. Include screenshots or animated GIFs if applicable.

**Possible Solution**

For a feature, skip this step. For a bug, include any suggestions on a fix or a reason for the bug.

**Context**

For a feature, skip this step. For a bug, provide any context or additional information that might be helpful. This can include the environment in which the issue occurred (device, OS, browser, specific software versions).

**Your Environment**

For a feature, skip this step. For a bug, specify any relevant details about your setup:

    Version used:
    Operating System and version:
    Browser and version:
    Other relevant software or hardware:

**Logs and Additional Information**

For a feature, skip this step. For a bug, include any error logs or any other information that might be relevant. You can format error logs or code snippets using Markdown code blocks.
```

## PR Template

Please use the following template to create a Pull Request:

```
**Overview**

Added a simple RAG functionality to the EAK-Copilot.

**Issue Reference:**

    - EPIC: setup baseline RAG #79
    - install postgres vectorDB extension #105
    - index baseline vector data in vectorDB #107
    - setup base retriever #97
    - setup /get_docs endpoint in backend #134
    - integrate rag to frontend #110
    - display RAG source URL in chat conversation #135
    - update README #112

**Changes Made**

    - Added rag/app/main.py to implement the /init_expert and /get_docs endpoints.
    - Added rag/app/models.py to implement the ResponseBody and RAGRequest model classes.
    - Added rag/app/test_semantic_search.py to run a simple semantic search query.
    - Added rag/Dockerfile to build the rag image.
    - Added rag/requirements.txt.
    - Updated docker-compose.yml to include the rag service.
    - Updated .env.example to include the postgresql port number.
    - Updated the README.md.

**Testing**

    - Tested endpoints manually through swagger docs at localhost:8010/docs.
    - Removed the db/data folder to index docs from scratch.
    - Ran rag/app/test_semantic_search.py.

**Screenshots**

![Eg. A GUI change](/screenshot.png)

**Additional Notes**

    - Crawling/Scraping/Indexing of fedlex.ch, ahv-iv.ch, zas.admin.ch and bsv.admin.ch will be implemented in a future sprint. For the moment only dummy data is indexed.
    - Auto data crawling/scraping/indexing will be configured from the main config.yaml file in the future (for the moment this process is manual).

**Requested Reviewers**

@tabee
```