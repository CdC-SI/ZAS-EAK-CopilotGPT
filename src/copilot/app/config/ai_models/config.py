from dataclasses import dataclass

from utils.enum import Client


@dataclass
class Base:
    name: str
    api: Client


@dataclass
class Embedding(Base):
    output_dimension: int


@dataclass
class LLM(Base):
    context_window: int
    max_output_tokens: int
