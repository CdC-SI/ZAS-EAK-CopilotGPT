from typing import List

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

    def rerank(self, query: str, documents: List[Document]) -> List[Document]:

        response = self.reranking_client.rerank(
            model=self.model,
            query=query,
            documents=documents,
            top_n=self.top_k,
        )

        logger.info(f"Reranking response: {response}")

        return response.results

    def reorder(self, query, documents: List[Document]) -> List[Document]:
        try:
            rerank_res = self.rerank(query, documents)
            rerank_idx = [res.index for res in rerank_res]
            reranked_docs = [documents[i] for i in rerank_idx]
            return reranked_docs[:self.top_k]

        except Exception as e:
            print(f"Reranker raised an exception: {e}")
            return documents[:self.top_k]
