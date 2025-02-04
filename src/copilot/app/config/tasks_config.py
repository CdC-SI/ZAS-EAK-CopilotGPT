from enum import Enum


class Tasks(Enum):
    RAG = "rag"
    QUERY_REWRITING = "query_rewriting"
    CONTEXTUAL_COMPRESSION = "contextual_compression"
    SOURCE_VALIDATION = "source_validation"
    CHAT_TITLE = "chat_title"
    MEMORY_SUMMARY = "memory_summary"
    SUMMARIZE_COMMAND = "summarize_agent"
    FUNCTION_CALL = "function_call"
    TOPIC_CHECK_AGENT = "topic_check_agent"
    INTENT_DETECTION = "intent_detection"
    HANDOFF_AGENT = "handoff_agent"
    PENSION_AGENT = "pension_agent"
