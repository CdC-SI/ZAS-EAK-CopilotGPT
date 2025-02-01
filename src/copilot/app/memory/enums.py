from enum import Enum


class MemoryType(Enum):
    BUFFER = "buffer"
    SUMMARY = "summary"
    BUFFER_SUMMARY = "buffer_summary"


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
