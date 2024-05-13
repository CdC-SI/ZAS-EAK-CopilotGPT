## Open-Source Collaboration Best Practices
Please refer yourself to the [best practices document](https://portal.collab.admin.ch/sites/602-eak-copilot/_layouts/15/WopiFrame.aspx?sourcedoc=%7B7AC07C75-D5A2-4107-BE9C-EF376BCCE416%7D&file=Open-Source%20project%20Collaboration%20%E2%80%93%20Best%20Practices%20Updated.pptx&action=default&IsList=1&ListId=%7BCDF81277-FBCD-4EB8-B449-D6E0BE5A98C9%7D&ListItemId=21) for guidelines on how to contribute to this project.

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