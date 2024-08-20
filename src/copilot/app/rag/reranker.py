from typing import List, Tuple

from config.clients_config import clientRerank

from schemas.document import Document

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Reranker:

    def __init__(self, model: str, top_k: int = 10):
        self.reranking_client = clientRerank
        self.model = model
        self.top_k = top_k

    def rerank(self, query: str, documents: List[Document]):
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

    def process_documents(self, query, documents: List[Document]) -> Tuple[List[Document], List[int]]:
        relevance_score = [0] * self.top_k  # Initialize relevance scores to 0

        try:
            reranked_res = self.rerank(query, documents)
            documents = [documents[item.index] for item in reranked_res]
            relevance_score = [item.relevance_score for item in reranked_res]

        finally:
            return documents[:self.top_k], relevance_score
