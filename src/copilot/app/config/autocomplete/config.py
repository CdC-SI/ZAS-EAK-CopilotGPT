from dataclasses import dataclass
from typing import Optional

from .matching import ExactMatching, LevenshteinMatching, TrigramMatching, SemanticMatching


@dataclass
class AutocompleteConfig:
    enabled: bool = True
    limit: int = 15

    exact_match: ExactMatching = ExactMatching()
    levenshtein_match: LevenshteinMatching = LevenshteinMatching()
    trigram_match: TrigramMatching = TrigramMatching()
    semantic_match: SemanticMatching = SemanticMatching()

    def __post_init__(self):
        if self.limit < 0:
            self.limit = 15

        if not isinstance(self.exact_match, ExactMatching):
            params = self.exact_match if isinstance(self.exact_match, dict) else {}
            self.exact_match = ExactMatching(**params)

        if not isinstance(self.levenshtein_match, LevenshteinMatching):
            params = self.levenshtein_match if isinstance(self.levenshtein_match, dict) else {}
            self.levenshtein_match = LevenshteinMatching(**params)

        if not isinstance(self.trigram_match, TrigramMatching):
            params = self.trigram_match if isinstance(self.trigram_match, dict) else {}
            self.trigram_match = TrigramMatching(**params)

        if not isinstance(self.semantic_match, SemanticMatching):
            params = self.semantic_match if isinstance(self.semantic_match, dict) else {}
            self.semantic_match = SemanticMatching(**params)
