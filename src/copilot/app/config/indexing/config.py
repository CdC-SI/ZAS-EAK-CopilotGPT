from dataclasses import dataclass
from config.ai_models.supported import Embedding as EmbeddingConfig


@dataclass
class IndexingConfig:
    enabled: bool = True
    auto_init: bool = False

    Embedding: EmbeddingConfig = EmbeddingConfig.TEXT_EMBEDDING_ADA_002

    def __post_init__(self):
        self.auto_init = self.enabled
        self.enabled = True

        if not isinstance(self.Embedding, EmbeddingConfig):
            self.Embedding = EmbeddingConfig[str(self.Embedding)]
