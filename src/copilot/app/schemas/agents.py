from typing import List
from pydantic import BaseModel, Field


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
    preferred_language: str = Field(
        ..., description="User's preferred language"
    )
    preferred_response_verbosity: str = Field(
        ..., description="Verbosity of assistant responses"
    )
    preferred_technical_depth: str = Field(
        ..., description="Technical level of assistnat responses"
    )


class TopicExpertiseLevels(BaseModel):
    ahv: str = Field(..., description="Expertise level in AHV")
    iv: str = Field(..., description="Expertise level in IV")
    general: str = Field(..., description="General expertise level")
    contributions: str = Field(..., description="Expertise in contributions")
    bankruptcy: str = Field(..., description="Expertise in bankruptcy")
    ahv_stabilisation_21: str = Field(
        ..., description="Expertise in AHV stabilisation 21"
    )
    ahv_services: str = Field(..., description="Expertise in AHV services")
    iv_services: str = Field(..., description="Expertise in IV services")
    complementary_services: str = Field(
        ..., description="Expertise in complementary services"
    )
    transitory_services: str = Field(
        ..., description="Expertise in transitory services"
    )
    loss_of_earnings_allowance: str = Field(
        ..., description="Expertise in loss of earnings allowance"
    )
    maternity_allowance: str = Field(
        ..., description="Expertise in maternity allowance"
    )
    allowance_for_the_other_parent: str = Field(
        ..., description="Expertise in allowance for the other parent"
    )
    support_allowance: str = Field(
        ..., description="Expertise in support allowance"
    )
    adoption_allowance: str = Field(
        ..., description="Expertise in adoption allowance"
    )
    international: str = Field(
        ..., description="Expertise in international matters"
    )
    family_allowances: str = Field(
        ..., description="Expertise in family allowances"
    )
    accident_insurance: str = Field(
        ..., description="Expertise in accident insurance"
    )
    occupational_benefits: str = Field(
        ..., description="Expertise in occupational benefits"
    )
    health_insurance: str = Field(
        ..., description="Expertise in health insurance"
    )
    annual_modifications: str = Field(
        ..., description="Expertise in annual modifications"
    )
    hearing_aids: str = Field(..., description="Expertise in hearing aids")
    akis_online_help: str = Field(
        ..., description="Expertise in AKIS online help"
    )
    lavs: str = Field(..., description="Expertise in LAVS")


class InteractionPreferences(BaseModel):
    avg_conversation_turns: int = Field(
        ..., description="Average number of conversation turns"
    )
    topic_expertise_levels: TopicExpertiseLevels


class LearningStyle(BaseModel):
    prefers_examples: bool = Field(
        ..., description="Does user prefer examples?"
    )
    prefers_step_by_step: bool = Field(
        ..., description="Does user prefer step-by-step explanations?"
    )
    visual_learner: bool = Field(..., description="Is user a visual learner?")


class HistoricalBehaviour(BaseModel):
    frequent_pain_points: List[str] = Field(
        ..., description="Frequent pain points between user and assistant"
    )
    successful_interactions: List[str] = Field(
        ...,
        description="Examples of successful interactions between user and assistant",
    )


class ContextualPreferences(BaseModel):
    common_questions: List[str] = Field(
        ..., description="List of common questions user has asked in the past"
    )
    common_topics: List[str] = Field(
        ..., description="List of broad topics user is interested in"
    )
    common_sources: List[str] = Field(
        ..., description="List of common sources user is interested in"
    )
    common_tags: List[str] = Field(
        ..., description="List of common tags (topics) user is interested in"
    )
    common_tools: List[str] = Field(
        ..., description="List of the tools user commonly uses"
    )
    frequently_accessed_documents: List[str] = Field(
        ..., description="List of frequently accessed documents"
    )


class UserPreferences(BaseModel):
    communication_preferences: CommunicationPreferences
    interaction_preferences: InteractionPreferences
    learning_style: LearningStyle
    historical_behaviour: HistoricalBehaviour
    contextual_preferences: ContextualPreferences
    confirmation_msg: str = Field(
        ...,
        description="A confirmation message to the user that the preference(s) are set",
    )
