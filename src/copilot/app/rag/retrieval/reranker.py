from typing import List, Tuple

from config.clients_config import Clients
from config.ai_models.supported import Reranker as RerankerModel

from database.models import Document

# Setup logging
from utils.logging import get_logger
logger = get_logger(__name__)


class Reranker:

    def __init__(self, model: RerankerModel, top_k: int = 10, enabled: bool = True):
        self.reranking_client = Clients.RERANKING.value
        self.model_name = model.value.name
        self.top_k = top_k
        self.enabled = enabled

    def _rerank(self, query: str, documents: List[str]):
        response = self.reranking_client.rerank(
            model=self.model_name,
            query=query,
            documents=documents,
            top_n=self.top_k,
        )
        return response.results

    def rerank(self, query, documents: List[Document]) -> Tuple[List[Document], List[int]]:
        if not self.enabled:
            logger.error("Reranker is not enabled.")
            return documents, [0] * len(documents)

        text_documents = [doc.text for doc in documents]
        logger.info(f"Reranking {len(documents)} documents...")

        reranked_res = self._rerank(query, text_documents)
        documents = [documents[item.index] for item in reranked_res]
        relevance_score = [item.relevance_score for item in reranked_res]

        logger.info(f"Finished reranking {len(documents)} documents.")
        return documents[:self.top_k], relevance_score