from enum import Enum


class Language(str, Enum):
    DEUTSCH = "de"
    FRANCAIS = "fr"
    ITALIANO = "it"


class Verbosity(str, Enum):
    CONCISE = "concise"
    VERBOSE = "verbose"


class TechnicalDepth(str, Enum):
    TECHNICAL = "technical"
    NON_TECHNICAL = "non-technical"


class ExpertiseLevel(str, Enum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class Source(str, Enum):
    AHV_IV_MEMENTO = "ahv_iv_memento"
    AHV_LERNBAUSTEIN_2024 = "ahv_lernbaustein_2024"
    AKIS = "akis"
    BSV = "bsv"
    EAK = "eak"
    FEDLEX = "fedlex"
    PRACTICAL_GUIDE_EAK_FZ = "practical_guide_eak_fz"
    SOZIALVERSICHERUNGEN = "sozialversicherungen"
    USER_PDF_UPLOAD = "user_pdf_upload"
    USER_EDIT = "user_edit"


class Tags(str, Enum):
    GENERAL = "general"
    CONTRIBUTIONS = "contributions"
    BANKRUPTCY = "bankruptcy"
    AHV_STABILISATION_21 = "ahv_stabilisation_21"
    AHV_SERVICES = "ahv_services"
    IV_SERVICES = "iv_services"
    COMPLEMENTARY_SERVICES = "complementary_services"
    TRANSITORY_SERVICES = "transitory_services"
    LOSS_OF_EARNINGS_ALLOWANCE = "loss_of_earnings_allowance"
    MATERNITY_ALLOWANCE = "maternity_allowance"
    ALLOWANCE_FOR_THE_OTHER_PARENT = "allowance_for_the_other_parent"
    SUPPORT_ALLOWANCE = "support_allowance"
    ADOPTION_ALLOWANCE = "adoption_allowance"
    INTERNATIONAL = "international"
    FAMILY_ALLOWANCES = "family_allowances"
    ACCIDENT_INSURANCE = "accident_insurance"
    OCCUPATIONAL_BENEFITS = "occupational_benefits"
    HEALTH_INSURANCE = "health_insurance"
    ANNUAL_MODIFICATIONS = "annual_modifications"
    HEARING_AIDS = "hearing_aids"
    AKIS_ONLINE_HELP = "akis_online_help"
    LAVS = "lavs"


class Tools(str, Enum):
    TRANSLATE = "translate"
    SUMMARIZE = "summarize"
    UPDATE_USER_PREFERENCES = "update_user_preferences"
    USER_FOLLOWUP_Q = "user_followup_q"
    DETERMINE_REDUCTION_RATE_AND_SUPPLEMENT = (
        "determine_reduction_rate_and_supplement"
    )
