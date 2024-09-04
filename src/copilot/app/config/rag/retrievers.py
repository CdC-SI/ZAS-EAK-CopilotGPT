from abc import ABC
from dataclasses import dataclass
from enum import Enum

from utils.enum import GetItemUpper, RetrieverType


@dataclass
class Retriever(ABC):
    type_: RetrieverType
    top_k: int

    def __post_init__(self):
        if self.top_k <= 0:
            self.top_k = 1


@dataclass
class TopK(Retriever):
    type_: RetrieverType = RetrieverType.TOP_K
    top_k: int = 100


@dataclass
class QueryRewriting(Retriever):
    type_: RetrieverType = RetrieverType.QUERY_REWRITING
    top_k: int = 10
    n_alt_queries: int = 3

    def __post_init__(self):
        super().__post_init__()
        if self.n_alt_queries < 1:
            self.n_alt_queries = 1


@dataclass
class ContextualCompression(Retriever):
    type_: RetrieverType = RetrieverType.CONTEXTUAL_COMPRESSION
    top_k: int = 4


@dataclass
class RAGFusion(Retriever):
    type_: RetrieverType = RetrieverType.RAG_FUSION
    top_k: int = 10
    n_alt_queries: int = 3
    rrf_k: int = 60

    def __post_init__(self):
        super().__post_init__()
        if self.n_alt_queries < 1:
            self.n_alt_queries = 1


@dataclass
class BM25(Retriever):
    type_: RetrieverType = RetrieverType.BM25
    top_k: int = 10
    k: float = 1.2
    b: float = 0.75


class Retrievers(Enum, metaclass=GetItemUpper):
    # BM25 = BM25
    RAG_FUSION = RAGFusion
    CONTEXTUAL_COMPRESSION = ContextualCompression
    QUERY_REWRITING = QueryRewriting
    TOP_K = TopK
