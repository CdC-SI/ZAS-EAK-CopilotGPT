from typing import Dict, AsyncGenerator
import json
from datetime import date
from dateutil.relativedelta import relativedelta
from langfuse.decorators import observe

from sqlalchemy.orm import Session
from schemas.chat import ChatRequest
from memory import MemoryService
from rag.retrievers import RetrieverClient
from utils.streaming import StreamingHandler
from schemas.agents import UserPreferences as UserPreferencesSchema
from agents.feedback import ask_user_feedback


from memory.enums import MessageRole
from commands.command_service import translation_service

from chat.messages import MessageBuilder
from llm.base import BaseLLM
from utils.streaming import Token
from utils.parsing import clean_text, parse_translation_args
from utils.logging import get_logger
from utils.user_preferences import update_user_preferences_in_db

logger = get_logger(__name__)


@observe(name="translate_tool")
async def translate_tool(
    request: ChatRequest,
    memory_service: MemoryService,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
    db: Session,
) -> AsyncGenerator[Token, None]:
    """
    Tool to translate text messages from conversation history.

    Parameters
    ----------
    request : ChatRequest
        The chat request containing user and conversation information
    memory_service : MemoryService
        Service for accessing chat memory
    message_builder : MessageBuilder
        Service for constructing messages
    llm_client : BaseLLM
        LLM client for processing
    db : Session
        Database session

    Yields
    ------
    Token
        Translated text tokens
    """

    args = await parse_translation_args(request, message_builder, llm_client)
    n_msg = args.get("n_msg", -1)
    target_lang = args.get("target_lang", "de")
    roles = args.get("roles", [MessageRole.USER, MessageRole.ASSISTANT])

    text = await memory_service.chat_memory.get_formatted_conversation(
        db,
        request.user_uuid,
        request.conversation_uuid,
        k_memory=n_msg,
        roles=roles,
    )
    cleaned_text = clean_text(text)

    translated_text = await translation_service.translate(
        cleaned_text, target_lang
    )

    yield translated_text


@observe(name="summarize_tool")
async def summarize_tool(
    request: ChatRequest,
    memory_service: MemoryService,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
    streaming_handler: StreamingHandler,
    db: Session,
) -> AsyncGenerator[Token, None]:
    """
    Tool to generate summaries of conversation history.

    Parameters
    ----------
    request : ChatRequest
        The chat request containing user and conversation information
    memory_service : MemoryService
        Service for accessing chat memory
    message_builder : MessageBuilder
        Service for constructing messages
    llm_client : BaseLLM
        LLM client for processing
    streaming_handler : StreamingHandler
        Handler for streaming responses
    db : Session
        Database session

    Yields
    ------
    Token
        Summary text tokens
    """
    conversational_memory = (
        await memory_service.chat_memory.get_formatted_conversation(
            db,
            request.user_uuid,
            request.conversation_uuid,
            k_memory=-1,
        )
    )

    messages = message_builder.build_agent_summarize_prompt(
        request.language,
        request.llm_model,
        request.query,
        conversational_memory,
    )

    event_stream = llm_client.call(
        messages,
        model="gpt-4o",
        stream=True,
        temperature=0.0,
        max_tokens=8192,
    )

    async for token in streaming_handler.generate_stream(event_stream):
        yield token


@observe(name="update_user_preferences")
async def update_user_preferences_tool(
    db: Session,
    request: ChatRequest,
    memory_service: MemoryService,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
) -> AsyncGenerator[Token, None]:
    """
    Updates user preferences based on conversation context.

    Parameters
    ----------
    db : Session
        Database session
    request : ChatRequest
        The chat request containing user information
    memory_service : MemoryService
        Service for accessing chat memory
    message_builder : MessageBuilder
        Service for constructing messages
    llm_client : BaseLLM
        LLM client for processing

    Yields
    ------
    Token
        Confirmation message tokens
    """
    conversational_memory = (
        await memory_service.chat_memory.get_formatted_conversation(
            db,
            request.user_uuid,
            request.conversation_uuid,
            k_memory=-1,
        )
    )

    messages = message_builder.build_update_user_preferences_prompt(
        language=request.language,
        llm_model="gpt-4o",
        query=request.query,
        conversational_memory=conversational_memory,
        response_schema=json.dumps(
            UserPreferencesSchema.model_json_schema(), indent=4
        ),
    )

    res = await llm_client.llm_client.beta.chat.completions.parse(
        model="gpt-4o",
        temperature=0.0,
        max_tokens=8192,
        messages=messages,
        response_format=UserPreferencesSchema,
    )

    user_preferences = res.choices[0].message.parsed
    message = update_user_preferences_in_db(
        db, request.user_uuid, user_preferences
    )
    yield Token.from_text(message)


# RAG tool
@observe(name="RAG_tool")
async def rag_tool(
    db: Session,
    request: ChatRequest,
    llm_client: BaseLLM,
    streaming_handler: StreamingHandler,
    retriever_client: RetrieverClient,
    message_builder: MessageBuilder,
    memory_service: MemoryService,
    sources: Dict,
) -> AsyncGenerator[Token, None]:
    """
    Retrieves and validates information using RAG (Retrieval-Augmented Generation).

    Parameters
    ----------
    db : Session
        Database session
    request : ChatRequest
        The chat request containing query and user information
    llm_client : BaseLLM
        LLM client for processing
    streaming_handler : StreamingHandler
        Handler for streaming responses
    retriever_client : RetrieverClient
        Client for retrieving documents
    message_builder : MessageBuilder
        Service for constructing messages
    memory_service : MemoryService
        Service for accessing chat memory
    sources : Dict
        Dictionary to store retrieved documents and sources

    Yields
    ------
    Token
        Response tokens and source information
    """

    from agents.agents import source_validator_agent
    from rag.rag_service import (
        rag_service,
    )  # TO DO: refactor to avoid circular import

    # Retrieve documents
    conversational_memory = (
        await (
            memory_service.chat_memory.get_formatted_conversation(
                db,
                request.user_uuid,
                request.conversation_uuid,
                request.k_memory,
            )
        )
    )

    documents = await rag_service.retrieve(
        db, request, retriever_client, conversational_memory
    )

    if not documents:
        async for token in ask_user_feedback(request, feedback_type="no_docs"):
            yield token
        return

    # Source validation
    validated_docs = []
    validated_sources = []
    invalid_docs = []

    async for (
        doc,
        llm_source_validation,
    ) in source_validator_agent.validate_sources(
        request,
        documents,
        llm_client,
        message_builder,
    ):
        if llm_source_validation.is_valid:
            validated_docs.append(doc)
            validated_sources.append(doc["url"])
        else:
            invalid_docs.append((doc, llm_source_validation.reason))

    # validated_docs = []
    # invalid_docs = [
    #     ({"text": "le splitting est considéré comme ayant été atteint.", "source": "source1", "tags": ["tag1", "tag2"], "subtopics": ["subtopic1", "subtopic2"], "summary": "summary", "id": 0}, "mauvais document"),
    #     ({"text": "le splitting est valide", "source": "source2", "tags": ["tag1", "tag2"], "subtopics": ["subtopic1", "subtopic2"], "summary": "summary", "id": "3"}, "document ambigu"), ({"text": "le splitting est invalide.", "source": "source2", "tags": ["tag1", "tag2"], "subtopics": ["subtopic1", "subtopic2"], "summary": "summary", "id": 4}, "bad doc"), ({"text": "hello hello", "source": "test_source", "tags": ["tag1", "tag2"], "subtopics": ["subtopic1", "subtopic2"], "summary": "summary", "id": "id"}, "bad BAD BADBAD doc"),
    # ]

    formatted_invalid_docs = "\n\n".join(
        [
            f"""<doc_{i}>{d[0]['text']}
Source: {d[0]['source']}
Tags: {d[0]['tags']}
Subtopics: {d[0]['subtopics']}
Summary: {d[0]['summary']}
Id: {d[0]['id']}
Reason: {d[1]}
</doc_{i}>"""
            for i, d in enumerate(invalid_docs, start=1)
        ]
    )

    # No more context docs after source validation
    if not validated_docs:

        user_preferences = (
            memory_service.chat_memory.cache.get_user_preferences(
                db, request.user_uuid
            )
        )

        async for token in ask_user_feedback(
            request=request,
            feedback_type="no_validated_docs",
            message_builder=message_builder,
            llm_client=llm_client,
            streaming_handler=streaming_handler,
            formatted_invalid_docs=formatted_invalid_docs,
            conversational_memory=conversational_memory,
            user_preferences=user_preferences,
        ):
            yield token
        return

    else:
        # Return top validated sources
        for source_url in validated_sources:
            yield Token.from_source(source_url)

    # Send RAG docs to LLM
    # ----> TO DO: keep track of doc_ids, source, tags, subtopics, summary, etc. for next search rounds (add this info in formatted_context_docs just below?) -> see sprint ticket
    # -> exclude docs that have already been validated
    # -> rerank cache of docs to retrieve faster if necessary
    formatted_context_docs = "\n\n".join(
        [
            f"<doc_{i}>{doc['text']}</doc_{i}>"
            for i, doc in enumerate(validated_docs, start=1)
        ]
    )

    messages = message_builder.build_chat_prompt(
        language=request.language,
        llm_model=request.llm_model,
        context_docs=formatted_context_docs,
        query=request.query,
        conversational_memory=conversational_memory,
        response_style=request.response_style,
        response_format=request.response_format,
    )

    # stream response
    event_stream = llm_client.call(messages)
    async for token in streaming_handler.generate_stream(event_stream):
        yield token

    sources["documents"] = validated_docs
    sources["source_urls"] = validated_sources

    # async for token in rag_service.process_rag(
    #     db,
    #     request,
    #     llm_client,
    #     streaming_handler,
    #     retriever_client,
    #     message_builder,
    #     memory_service,
    #     sources,
    # ):
    #     yield token


@observe(name="FAK_EAK_calculate_reduction_rate_and_supplement_tool")
def determine_reduction_rate_and_supplement_tool(
    date_of_birth: str, retirement_date: str, average_annual_income: float
) -> Dict:
    """
    Calculate the reduction rate or pension supplement for women of the transitional generation.

    Parameters
    ----------
    date_of_birth : str
        Birth date in YYYY-MM-DD format for women born between 1961-1969
    retirement_date : str
        Planned retirement date in YYYY-MM-DD format
    average_annual_income : float
        Average annual income in CHF (minimum 0)

    Returns
    -------
    Dict
        Dictionary containing either:
        - {'ReductionRate': float} : Reduction rate percentage
        - {'PensionSupplement': float} : Monthly pension supplement amount
        - {'NotEligible': str} : URL with eligibility information
        - {'InvalidIncome': str} : Error message for invalid income
        - {'InvalidAnticipationYears': str} : URL with valid anticipation periods
    """
    date_of_birth = date.fromisoformat(date_of_birth)
    retirement_date = date.fromisoformat(retirement_date)
    average_annual_income = float(average_annual_income)

    # Get the year of birth
    year_of_birth = date_of_birth.year

    # Check if the woman is part of the transitional generation
    if not (1961 <= year_of_birth <= 1969):
        logger.info("------NOT ELIGIBLE")
        return {
            "NotEligible": "https://www.eak.admin.ch/eak/fr/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html"
        }

    # Calculate the age at retirement in years and months
    age_delta = relativedelta(retirement_date, date_of_birth)
    age_years = age_delta.years
    age_months = age_delta.months
    age_total_months = age_years * 12 + age_months

    # Reference ages for each year of birth (in months)
    reference_ages_months = {
        1961: (64 * 12) + 3,  # 64 years + 3 months
        1962: (64 * 12) + 6,  # 64 years + 6 months
        1963: (64 * 12) + 9,  # 64 years + 9 months
        1964: 65 * 12,  # 65 years
        1965: 65 * 12,  # 65 years
        1966: 65 * 12,  # 65 years
        1967: 65 * 12,  # 65 years
        1968: 65 * 12,  # 65 years
        1969: 65 * 12,  # 65 years
    }

    reference_age_months = reference_ages_months[year_of_birth]

    # Determine income bracket and base supplement
    if average_annual_income <= 60480:
        income_bracket = 1
        base_supplement = 160
    elif 60481 <= average_annual_income <= 75600:
        income_bracket = 2
        base_supplement = 100
    elif average_annual_income >= 75601:
        income_bracket = 3
        base_supplement = 50
    else:
        logger.info("------INVALID INCOME")
        return {"InvalidIncome": ""}

    # Check if retiring at or after the reference age
    if age_total_months >= reference_age_months:
        # Pension supplement percentages based on year of birth
        supplement_percentages = {
            1961: 25,
            1962: 50,
            1963: 75,
            1964: 100,
            1965: 100,
            1966: 81,
            1967: 63,
            1968: 44,
            1969: 25,
        }
        percentage = supplement_percentages[year_of_birth]
        supplement = base_supplement * (percentage / 100)
        logger.info("------PENSION SUPPLEMENT")
        return {"PensionSupplement": supplement}  # per month
    else:
        # Calculate anticipation months
        anticipation_months = reference_age_months - age_total_months

        # Convert anticipation months to anticipation years
        anticipation_years = anticipation_months / 12

        # Round anticipation years to nearest integer
        anticipation_years_int = int(round(anticipation_years))

        if anticipation_years_int not in [1, 2, 3]:
            logger.info("------INVALID ANTICIPATION YEARS")
            return {
                "InvalidAnticipationYears": "https://www.eak.admin.ch/eak/fr/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html"
            }

        # Reduction rates table
        reduction_rates = {
            1: {1: 0.0, 2: 2.5, 3: 3.5},  # 1 year anticipation
            2: {1: 2.0, 2: 4.5, 3: 6.5},  # 2 years anticipation
            3: {1: 3.0, 2: 6.5, 3: 10.5},  # 3 years anticipation
        }

        # Retrieve the reduction rate
        reduction_rate = reduction_rates[anticipation_years_int][
            income_bracket
        ]
        return {"ReductionRate": reduction_rate}


def _format_reference_age(months: int) -> str:
    """
    Convert total months into a formatted string of years and months.

    Parameters
    ----------
    months : int
        Total number of months to convert

    Returns
    -------
    str
        Formatted string in the format "X years" or "X years and Y months"
    """
    years = months // 12
    remaining_months = months % 12
    if remaining_months == 0:
        return f"{years} years"
    return f"{years} years and {remaining_months} months"


@observe(name="PENSION_determine_reference_age_tool")
def determine_reference_age_tool(date_of_birth: str) -> Dict:
    """
    Determine the reference age for women of the transitional generation.

    Parameters
    ----------
    date_of_birth : str
        Birth date in YYYY-MM-DD format

    Returns
    -------
    Dict
        Dictionary containing either:
        - {'ReferenceAge': str} : Formatted reference age and pension start date
        - {'NotEligible': str} : Message or URL explaining ineligibility
    """
    date_of_birth = date.fromisoformat(date_of_birth)
    year_of_birth = date_of_birth.year

    # Check if the woman is part of the transitional generation
    if not (1961 <= year_of_birth <= 1969):
        logger.info("------NOT ELIGIBLE")
        return {
            "NotEligible": "https://www.eak.admin.ch/eak/fr/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html"
        }

    reference_ages_months = {
        1960: ((64 * 12), 2024),  # 64 years in 2024
        1961: ((64 * 12) + 3, 2025),  # 64 years + 3 months in 2025
        1962: ((64 * 12) + 6, 2026),  # 64 years + 6 months in 2026
        1963: ((64 * 12) + 9, 2027),  # 64 years + 9 months in 2027
        1964: (65 * 12, 2028),  # 65 years in 2028
        1965: (65 * 12,),  # 65 years
        1966: (65 * 12,),  # 65 years
        1967: (65 * 12,),  # 65 years
        1968: (65 * 12,),  # 65 years
        1969: (65 * 12,),  # 65 years
    }

    if year_of_birth not in reference_ages_months:
        return {"NotEligible": "Year of birth not in transitional generation."}

    reference_age_months = reference_ages_months[year_of_birth][0]
    formatted_age = _format_reference_age(reference_age_months)
    pension_start_date = date_of_birth + relativedelta(
        months=reference_age_months
    )

    response = f"Your reference age is {formatted_age}. More precisely, you are entitled to an unreduced AHV pension from: {pension_start_date}"

    return {"ReferenceAge": response}


@observe(name="PENSION_estimate_pension_tool")
def estimate_pension_tool():
    pass


# FAK-EAK tools
@observe(name="FAK_EAK_determine_child_benefits_eligibility_tool")
def determine_child_benefits_eligibility_tool():
    pass
