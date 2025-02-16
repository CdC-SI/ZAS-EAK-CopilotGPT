from typing import List
from pydantic import BaseModel, Field

from enums.agents import (
    Language,
    Verbosity,
    TechnicalDepth,
    ExpertiseLevel,
    Source,
    Tags,
    Tools,
)


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
    preferred_language: Language = Field(
        default=Language.DEUTSCH,
        description="User's preferred language",
        choices=[lang.value for lang in Language],
    )
    preferred_response_verbosity: Verbosity = Field(
        default=Verbosity.CONCISE,
        description="Verbosity of assistant responses",
        choices=[verb.value for verb in Verbosity],
    )
    preferred_technical_depth: TechnicalDepth = Field(
        default=TechnicalDepth.TECHNICAL,
        description="Technical level of assistant responses",
        choices=[tech.value for tech in TechnicalDepth],
    )


class TopicExpertiseLevels(BaseModel):
    ahv: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise level in AHV",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    iv: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise level in IV",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    general: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="General expertise level",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    contributions: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in contributions",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    bankruptcy: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in bankruptcy",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    ahv_stabilisation_21: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in AHV stabilisation 21",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    ahv_services: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in AHV services",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    iv_services: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in IV services",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    complementary_services: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in complementary services",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    transitory_services: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in transitory services",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    loss_of_earnings_allowance: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in loss of earnings allowance",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    maternity_allowance: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in maternity allowance",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    allowance_for_the_other_parent: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in allowance for the other parent",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    support_allowance: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in support allowance",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    adoption_allowance: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in adoption allowance",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    international: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in international matters",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    family_allowances: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in family allowances",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    accident_insurance: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in accident insurance",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    occupational_benefits: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in occupational benefits",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    health_insurance: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in health insurance",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    annual_modifications: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in annual modifications",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    hearing_aids: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in hearing aids",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    akis_online_help: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in AKIS online help",
        choices=[exp.value for exp in ExpertiseLevel],
    )
    lavs: ExpertiseLevel = Field(
        default=ExpertiseLevel.NOVICE,
        description="Expertise in LAVS",
        choices=[exp.value for exp in ExpertiseLevel],
    )


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
        ...,
        description="Frequent pain points between user and assistant",
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
        ...,
        description="List of common sources user is interested in",
        choices=[source.value for source in Source],
    )
    common_tags: List[str] = Field(
        ...,
        description="List of common tags (topics) user is interested in",
        choices=[tag.value for tag in Tags],
    )
    frequently_accessed_documents: List[str] = Field(
        ..., description="List of frequently accessed documents"
    )


class ToolPreferences(BaseModel):
    common_tools: List[str] = Field(
        ...,
        description="List of the tools user commonly uses",
        choices=[tool.value for tool in Tools],
    )


class UserPreferences(BaseModel):
    communication_preferences: CommunicationPreferences
    interaction_preferences: InteractionPreferences
    learning_style: LearningStyle
    historical_behaviour: HistoricalBehaviour
    contextual_preferences: ContextualPreferences
    tool_preferences: ToolPreferences
    confirmation_msg: str = Field(
        ...,
        description="A confirmation message to the user that the preference(s) are set",
    )
