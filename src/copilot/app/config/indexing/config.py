from dataclasses import dataclass
from config.ai_models.supported import Embedding as EmbeddingConfig


@dataclass
class IndexingConfig:
    enabled: bool = False

    Embedding: EmbeddingConfig = EmbeddingConfig.TEXT_EMBEDDING_ADA_002

    def __post_init__(self):
        if not isinstance(self.Embedding, EmbeddingConfig):
            self.Embedding = EmbeddingConfig[str(self.Embedding)]
