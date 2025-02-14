from typing import List
from pydantic import BaseModel


class TopicCheck(BaseModel):
    on_topic: bool


class IntentDetection(BaseModel):
    intent: str
    followup_question: str


class SourceSelection(BaseModel):
    inferred_sources: List[str]


class TagSelection(BaseModel):
    inferred_tags: List[str]


class AgentHandoff(BaseModel):
    agent: str


class FunctionCall(BaseModel):
    function_call: str


class ParseTranslateArgs(BaseModel):
    arg_values: List[str]


class MultipleSourceValidation(BaseModel):
    sources: List[str]
    is_valid: bool


class UniqueSourceValidation(BaseModel):
    is_partial: bool
    is_valid: bool
    reason: str


class CommunicationPreferences(BaseModel):
    preferred_language: str
    preferred_response_verbosity: str
    preferred_technical_depth: str


class TopicExpertiseLevels(BaseModel):
    ahv: str
    iv: str


class InteractionPreferences(BaseModel):
    avg_conversation_turns: int
    topic_expertise_levels: TopicExpertiseLevels


class LearningStyle(BaseModel):
    prefers_examples: bool
    prefers_step_by_step: bool
    visual_learner: bool


class HistoricalBehaviour(BaseModel):
    frequent_pain_points: List[str]
    successful_interactions: List[str]


class ContextualPreferences(BaseModel):
    common_questions: List[str]
    common_topics: List[str]
    common_sources: List[str]
    common_tags: List[str]
    common_tools: List[str]
    frequently_accessed_documents: List[str]
