from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

client = OpenAI()

tools = [{
    "type": "function",
    "function": {
        "name": "get_invalidite",
        "description": "Calculates the invalidity rate based on the beneficiary's income and required financial indicators.",
        "strict": True,
        "parameters": {
            "type": "object",
            "required": [
                "benef"
            ],
            "properties": {
                "benef": {
                    "type": "object",
                    "description": "A JSON object representing the beneficiary's data.",
                    "properties": {
                        "abattement": {
                            "type": "number",
                            "description": "Flat rate deduction on income.  if not mentioned in description all properties' values = 0"
                        },
                        "diminution": {
                            "type": "number",
                            "description": "Percentage reduction in work capacity.  if not mentioned in description all properties' values = 0"
                        },
                        "ess": {
                            "type": "number",
                            "description": "Year of reference (disability evaluation year)."
                        },
                        "ex": {
                            "type": "object",
                            "description": "Exigible wage data for the beneficiary.",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "Year of the exigible wage."
                                },
                                "branche": {
                                    "type": "string",
                                    "description": "Economic sector of the exigible wage. string always start with a capital letter unless a number"
                                },
                                "niveau_comp": {
                                    "type": "number",
                                    "description": "Competence level associated with the exigible wage."
                                },
                                "salaire": {
                                    "type": "number",
                                    "description": "Exigible salary amount."
                                }
                            },
                            "additionalProperties": False,
                            "required": [
                                "année",
                                "branche",
                                "niveau_comp",
                                "salaire"
                            ]
                        },
                        "horaire": {
                            "type": "number",
                            "description": "Occupation rate as a percentage."
                        },
                        "salaire_as": {
                            "type": "object",
                            "description": "Pre-disability salary data.",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "Year of recorded salary."
                                },
                                "salaire": {
                                    "type": "number",
                                    "description": "Salary amount before health impairment."
                                }
                            },
                            "additionalProperties": False,
                            "required": [
                                "année",
                                "salaire"
                            ]
                        },
                        "sainv": {
                            "type": "object",
                            "description": "Salary data pre-health impairment. if not mentioned in description all properties' values = 0",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "Year of the pre-health impairment salary."
                                },
                                "branche": {
                                    "type": "string",
                                    "description": "Economic sector relevant to the pre-health impairment salary."
                                },
                                "niveau_comp": {
                                    "type": "number",
                                    "description": "Competence level related to the pre-health impairment salary."
                                },
                                "salaire": {
                                    "type": "number",
                                    "description": "pre-health impairment salary amount."
                                }
                            },
                            "additionalProperties": False,
                            "required": [
                                "année",
                                "branche",
                                "niveau_comp",
                                "salaire"
                            ]
                        },
                        "salaire_effectif": {
                            "type": "object",
                            "description": "Current effective salary data. if not mentioned in description all properties' values = 0",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "Year of the effective salary."
                                },
                                "salaire": {
                                    "type": "number",
                                    "description": "Current effective salary amount."
                                }
                            },
                            "additionalProperties": False,
                            "required": [
                                "année",
                                "salaire"
                            ]
                        },
                        "sexe": {
                            "type": "string",
                            "description": "Gender of the beneficiary (e.g. 'homme', 'femme')."
                        }
                    },
                    "additionalProperties": False,
                    "required": [
                        "abattement",
                        "diminution",
                        "ess",
                        "ex",
                        "horaire",
                        "salaire_as",
                        "sainv",
                        "salaire_effectif",
                        "sexe"
                    ]
                }
            },
            "additionalProperties": False
        }
    }
}]
