from typing import Dict, AsyncGenerator
from dataclasses import dataclass
from datetime import date
from dateutil.relativedelta import relativedelta
from langfuse.decorators import observe

from commands.command_service import TranslationService
from chat.messages import MessageBuilder
from llm.base import BaseLLM
from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CommandResult:
    success: bool
    message: str
    source: str = ""


class CommandFunctions:
    def __init__(
        self,
        translation_service: TranslationService,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
    ):
        self.translation_service = translation_service
        self.message_builder = message_builder
        self.llm_client = llm_client

    @observe(name="translate_tool")
    async def translate_conversation(
        self, text: str, target_lang: str, mode: str = "all", n_msg: int = -1
    ) -> CommandResult:
        """
        Translates conversation text to target language
        Parameters:
        - text: The text to translate
        - target_lang: Target language code (e.g., 'de', 'fr', 'it')
        - mode: Translation mode ('all' or 'last')
        - n_msg: Number of messages to translate when mode is 'last'
        Returns: CommandResult with translation or error message
        """
        try:
            translated_text = await self.translation_service.translate(
                text, target_lang
            )
            # return CommandResult(
            #     success=True,
            #     message=translated_text,
            #     source="DeepL Translation Command Service"
            # )
            return {"translated_text": translated_text}
        except Exception as e:
            # return CommandResult(
            #     success=False,
            #     message="Sorry, an error occurred during translation. Please try again later.",
            #     source=""
            # )
            logger.info(e)
            return
            # return f"Unknown command: {request.command}"

    @observe(name="summarize_tool")
    async def summarize_conversation(
        self,
        text: str,
        mode: str = "all",
        n_msg: int = -1,
        style: str = "concise",
    ) -> CommandResult:
        """
        Summarizes conversation text
        Parameters:
        - text: The conversation text to summarize
        - mode: Summary mode ('all', 'last', or 'highlights')
        - n_msg: Number of messages to summarize when mode is 'last'
        - style: Summary style ('formal', 'concise', 'detailed')
        Returns: CommandResult with summary or error message
        """
        try:
            messages = self.message_builder.build_summarize_prompt(
                language="de",
                llm_model="gpt-4o-mini",
                command="/summarize",
                input_text=text,
                mode=mode,
                style=style,
            )

            response = await self.llm_client.call(messages)
            summary = "".join([chunk.content for chunk in response])

            return CommandResult(
                success=True,
                message=summary,
                source="AI Summary Command Service",
            )
        except Exception as e:
            logger.info(e)
            return CommandResult(
                success=False,
                message="Sorry, an error occurred during summarization. Please try again later.",
                source="",
            )


# RAG tool
@observe(name="RAG_tool")
async def rag_tool(
    db,
    request,
    llm_client,
    streaming_handler,
    retriever_client,
    message_builder,
    memory_service,
    sources,
) -> AsyncGenerator[str, None]:

    from rag.rag_service import rag_service

    async for token in rag_service.process_rag(
        db,
        request,
        llm_client,
        streaming_handler,
        retriever_client,
        message_builder,
        memory_service,
        sources,
    ):
        yield token


# Pension Agent tools
@observe(name="FAK_EAK_calculate_reduction_rate_and_supplement_tool")
def determine_reduction_rate_and_supplement(
    date_of_birth: str, retirement_date: str, average_annual_income: float
) -> Dict:
    """Calculate the reduction rate or pension supplement for women of the transitional generation.

    Parameters:
    - date_of_birth (str) - Birth date in YYYY-MM-DD format for women born between 1961-1969
    - retirement_date (str) - Planned retirement date in YYYY-MM-DD format
    - average_annual_income (float) - Average annual income in CHF (minimum 0)

    Returns:
    - Dict - A dictionary containing the calculated reduction rate, pension supplement or error message

    Examples:
    - date_of_birth: "1965-06-15"
    - retirement_date: "2030-06-15"
    - average_annual_income: 70000.00
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
    years = months // 12
    remaining_months = months % 12
    if remaining_months == 0:
        return f"{years} years"
    return f"{years} years and {remaining_months} months"


@observe(name="PENSION_determine_reference_age_tool")
def determine_reference_age(date_of_birth: str) -> Dict:
    """
    Determine the reference age for women born between 1961-1969 (transitional generation).
    Returns a dictionary with formatted reference age string.
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
def estimate_pension():
    pass


# FAK-EAK tools
@observe(name="FAK_EAK_determine_child_benefits_eligibility_tool")
def determine_child_benefits_eligibility():
    pass
