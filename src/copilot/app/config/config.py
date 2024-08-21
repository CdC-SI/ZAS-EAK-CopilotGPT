import os
from dotenv import load_dotenv
from abc import ABC
from dataclasses import dataclass
from enum import Enum

from typing import Dict


@dataclass
class Matching:
    limit: int


@dataclass
class MatchingThreshold(Matching):
    threshold: float


@dataclass
class MatchingMetric(Matching):
    metric: str


@dataclass
class AutocompleteConfig:
    enabled: bool
    limit: int
    matching_methods: Dict[str, Matching]


@dataclass
class Retrievers(ABC):
    top_k: int
    params: Dict[str, float]


@dataclass
class GenRetrievers(Retrievers):
    n_alt_gen: int


@dataclass
class RAGConfig:
    enabled: bool


@dataclass
class IndexingConfig:
    enabled: bool
    dev_mode: bool


@dataclass
class Config:
    autocomplete: AutocompleteConfig
