from typing import List, Tuple

from config.clients_config import clientRerank

from database.models import Document

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Reranker:

    def __init__(self, model: str, top_k: int = 10):
        self.reranking_client = clientRerank
        self.model = model
        self.top_k = top_k

    def _rerank(self, query: str, documents: List[str]):
        try:
            response = self.reranking_client.rerank(
                model=self.model,
                query=query,
                documents=documents,
                top_n=self.top_k,
            )
            return response.results

        except Exception as e:
            logger.error(f"Reranker raised an exception: {e}")

    def rerank(self, query, documents: List[Document]) -> Tuple[List[Document], List[int]]:
        relevance_score = [0] * self.top_k  # Initialize relevance scores to 0
        text_documents = [doc["text"] for doc in documents]

        logger.info(f"Reranking {len(documents)} documents...")

        try:
            reranked_res = self._rerank(query, text_documents)
            documents = [documents[item.index] for item in reranked_res]
            relevance_score = [item.relevance_score for item in reranked_res]

        finally:
            logger.info(f"Finished reranking {len(documents)} documents.")
            return documents[:self.top_k], relevance_score
