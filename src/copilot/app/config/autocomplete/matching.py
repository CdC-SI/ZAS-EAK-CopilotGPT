from abc import ABC
from dataclasses import dataclass, field
from utils.enum import VectorMetric


@dataclass
class Matching(ABC):
    limit: int = 10

    def __post_init__(self):
        if self.limit < 0:
            self.limit = 1


@dataclass
class ExactMatching(Matching):
    pass


@dataclass
class LevenshteinMatching(Matching):
    limit: int = 50
    threshold: int = 10

    def __post_init__(self):
        super().__post_init__()
        if self.threshold < 0:
            self.threshold = 0


@dataclass
class TrigramMatching(Matching):
    threshold: float = 0.4

    def __post_init__(self):
        super().__post_init__()
        if not 0 <= self.threshold <= 1:
            self.threshold = 0.4


@dataclass
class SemanticMatching(Matching):
    metric: VectorMetric = field(default=VectorMetric.COSINE_SIMILARITY)

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.metric, VectorMetric):
            self.metric = VectorMetric[str(self.metric)]


class MatchingType:
    exact = ExactMatching
    levenshtein = LevenshteinMatching
    trigram = TrigramMatching
    semantic = SemanticMatching
