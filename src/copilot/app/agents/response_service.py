from enum import Enum
from typing import Dict, Any


class ResponseType(Enum):
    PENSION_SUPPLEMENT = "PensionSupplement"
    REDUCTION_RATE = "ReductionRate"
    NOT_ELIGIBLE = "NotEligible"
    INVALID_INCOME = "InvalidIncome"
    INVALID_ANTICIPATION_YEARS = "InvalidAnticipationYears"


class CalculationResponseService:
    """
    Service for handling calculation response messages in different languages.

    This class manages response messages for pension-related calculations,
    supporting multiple languages and different types of responses.

    Attributes
    ----------
    _SOURCE_URLS : dict
        URLs for pension documentation in different languages
    _RESPONSE_MESSAGES : dict
        Message templates for different response types and languages
    DEFAULT_LANGUAGE : str
        Fallback language code
    """

    _SOURCE_URLS = {
        "de": "https://www.eak.admin.ch/eak/de/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html",
        "fr": "https://www.eak.admin.ch/eak/fr/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html",
        "it": "https://www.eak.admin.ch/eak/it/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html",
    }

    _RESPONSE_MESSAGES = {
        ResponseType.PENSION_SUPPLEMENT: {
            "de": "Ihre monatliche Rentenzulage beträgt {:.2f} CHF.",
            "fr": "Votre supplément de rente mensuel s'élève à {:.2f} CHF.",
            "it": "Il suo supplemento mensile di rendita ammonta a {:.2f} CHF.",
        },
        ResponseType.REDUCTION_RATE: {
            "de": "Ihr Kürzungssatz beträgt {:.1f}%.",
            "fr": "Votre taux de réduction est de {:.1f}%.",
            "it": "Il suo tasso di riduzione è del {:.1f}%.",
        },
        ResponseType.NOT_ELIGIBLE: {
            "de": "Sie erfüllen die Anspruchsvoraussetzungen nicht. Weitere Informationen finden Sie unter: [Tiefere Kürzungssätze bei Vorbezug]({})",
            "fr": "Vous ne remplissez pas les conditions d'éligibilité. Pour plus d'informations, consultez: [Taux de réduction favorable en cas d’anticipation de la rente]({})",
            "it": "Non soddisfa i requisiti di ammissibilità. Per maggiori informazioni, consulti: [Aliquote di riduzione ridotte in caso di anticipazione della rendita]({})",
        },
        ResponseType.INVALID_INCOME: {
            "de": "Das angegebene Einkommen ist ungültig. {}",
            "fr": "Le revenu indiqué n'est pas valide. {}",
            "it": "Il reddito indicato non è valido. {}",
        },
        ResponseType.INVALID_ANTICIPATION_YEARS: {
            "de": "Sie erfüllen die Voraussetzungen für einen Rentenvorbezug nicht. Weitere Informationen: [Tiefere Kürzungssätze bei Vorbezug]({})",
            "fr": "Vous ne remplissez pas les conditions pour une retraite anticipée. Plus d'informations: [Taux de réduction favorable en cas d’anticipation de la rente]({})",
            "it": "Non soddisfa i requisiti per il pensionamento anticipato. Maggiori informazioni: [Aliquote di riduzione ridotte in caso di anticipazione della rendita]({})",
        },
    }

    DEFAULT_LANGUAGE = "de"

    @classmethod
    def get_response_message(
        cls, calculation_result: Dict[str, Any], language: str
    ) -> str:
        """
        Format response message based on calculation result and language.

        Parameters
        ----------
        calculation_result : Dict[str, Any]
            Dictionary containing single key-value pair with response type and value
        language : str
            Language code for the response message

        Returns
        -------
        tuple
            Formatted message string and source URL for documentation

        Notes
        -----
        Returns "Invalid calculation result" for invalid input
        """
        if not calculation_result or len(calculation_result) != 1:
            return "Invalid calculation result"

        response_type = next(iter(calculation_result))
        value = calculation_result[response_type]

        try:
            response_type = ResponseType(response_type)
            messages = cls._RESPONSE_MESSAGES[response_type]
            message_template = messages.get(
                language, messages[cls.DEFAULT_LANGUAGE]
            )

            # Handle URL formatting for specific response types
            if response_type in [
                ResponseType.NOT_ELIGIBLE,
                ResponseType.INVALID_ANTICIPATION_YEARS,
            ]:
                value = value.replace("/fr/", f"/{language}/")

            source = cls._SOURCE_URLS.get(
                language, cls._SOURCE_URLS[cls.DEFAULT_LANGUAGE]
            )

            return message_template.format(value), source
        except (KeyError, ValueError):
            return "Unknown response type"


calculation_response_service = CalculationResponseService()
