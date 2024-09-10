from enum import Enum, EnumMeta, auto


class GetItemUpper(EnumMeta):
    def __getitem__(self, key: str):
        return super().__getitem__(key.upper())


class VectorMetric(Enum, metaclass=GetItemUpper):
    COSINE_SIMILARITY = "<=>"
    L1_DISTANCE = "<+>"
    L2_DISTANCE = "<->"
    NEGATIVE_INNER_PRODUCT = "<#>"


class Client(Enum):
    OPENAI = auto()
    COHERE = auto()
    # GROQ = auto()
    # LOCAL = auto()


class RetrieverType(Enum):
    TOP_K = auto()
    QUERY_REWRITING = auto()
    CONTEXTUAL_COMPRESSION = auto()
    RAG_FUSION = auto()
    BM25 = auto()
