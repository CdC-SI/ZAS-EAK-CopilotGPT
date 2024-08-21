import os
from dotenv import load_dotenv
from abc import ABC
from dataclasses import dataclass
from enum import Enum


class SimilarityMetric(Enum):
    CosineSimilarity = "<=>"
    l1Distance = "<+>"
    l2Distance = "<->"
    NegativeInnerProduct = "<#>"


# Database connection parameters
@dataclass
class AutocompleteConfiguration:
    enabled: bool
    limit: int

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()



