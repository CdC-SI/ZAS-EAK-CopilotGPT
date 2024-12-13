from typing import List, Tuple

from config.clients_config import clientRerank
from config.base_config import rag_config

from database.models import Document

from langfuse.decorators import observe

# Setup logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Reranker:

    def __init__(self, model: str):
        self.reranking_client = clientRerank
        self.model = model

    async def _rerank(self, query: str, documents: List[str], top_k: int):
        try:
            response = await self.reranking_client.rerank(
                model=self.model,
                query=query,
                documents=documents,
                top_n=top_k,
            )
            return response.results

        except Exception as e:
            logger.error(f"Reranker raised an exception: {e}")

    @observe(name="rerank")
    async def rerank(
        self,
        query,
        documents: List[Document],
        top_k: int = rag_config["retrieval"]["reranking_params"]["top_k"],
    ) -> Tuple[List[Document], List[int]]:
        relevance_score = [0] * top_k  # Initialize relevance scores to 0
        text_documents = [doc["text"] for doc in documents]

        logger.info("Reranking %s documents...", len(documents))

        try:
            reranked_res = await self._rerank(query, text_documents, top_k)
            documents = [documents[item.index] for item in reranked_res]
            relevance_score = [item.relevance_score for item in reranked_res]

        finally:
            logger.info("Finished reranking %s documents.", len(documents))
            return documents[:top_k], relevance_score
