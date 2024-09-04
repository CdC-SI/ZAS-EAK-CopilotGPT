from dataclasses import dataclass, field
from typing import Optional, List

from .ai_models.supported import Reranker
from config.rag.retrievers import Retriever, Retrievers

from utils.enum import VectorMetric


@dataclass
class RerankingConfig:
    enabled: bool = True
    top_k: int = 5
    model: Reranker = Reranker.RERANK_MULTILINGUAL_V3_0

    def __post_init__(self):
        if self.top_k < 0:
            self.top_k = 5

        if not isinstance(self.model, Reranker):
            self.model = Reranker[str(self.model)]


@dataclass
class RetrievalConfig:
    top_k: int = 10
    metric: VectorMetric = VectorMetric.COSINE_SIMILARITY

    retrievers: List[Retriever] = field(default_factory=lambda: [Retrievers.TOP_K.value()])
    Reranking: RerankingConfig = RerankingConfig()

    def __post_init__(self):
        if self.top_k < 0:
            self.top_k = 10

        if not isinstance(self.metric, VectorMetric):
            self.metric = VectorMetric[str(self.metric)]

        if isinstance(self.retrievers, list) and len(self.retrievers) > 0:
            if not isinstance(self.retrievers[0], Retriever):
                retrievers = []
                for retriever in self.retrievers:
                    name = retriever
                    params = {}
                    if isinstance(retriever, dict):
                        name = str(list(retriever.keys())[0])
                        params = retriever.get(name)
                        if not isinstance(params, dict):
                            params = {}

                    item = Retrievers[name].value(**params)
                    retrievers.append(item)
                self.retrievers = retrievers
        else:
            self.retrievers = [Retrievers.TOP_K.value()]  # Default value

        if not isinstance(self.Reranking, RerankingConfig):
            params = self.Reranking if isinstance(self.Reranking, dict) else {'enabled': bool(self.Reranking)}
            self.Reranking = RerankingConfig(**params)
