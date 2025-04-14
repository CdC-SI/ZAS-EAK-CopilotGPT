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
        "strict": true,
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
                            "description": "Flat rate deduction on income."
                        },
                        "diminution": {
                            "type": "number",
                            "description": "Percentage reduction in work capacity."
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
                                    "description": "Economic sector of the exigible wage."
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
                            "additionalProperties": false,
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
                            "additionalProperties": false,
                            "required": [
                                "année",
                                "salaire"
                            ]
                        },
                        "sainv": {
                            "type": "object",
                            "description": "Salary data post-health impairment.",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "Year of the post-health impairment salary."
                                },
                                "branche": {
                                    "type": "string",
                                    "description": "Economic sector relevant to the post-health impairment salary."
                                },
                                "niveau_comp": {
                                    "type": "number",
                                    "description": "Competence level related to the post-health impairment salary."
                                },
                                "salaire": {
                                    "type": "number",
                                    "description": "Post-health impairment salary amount."
                                }
                            },
                            "additionalProperties": false,
                            "required": [
                                "année",
                                "branche",
                                "niveau_comp",
                                "salaire"
                            ]
                        },
                        "salaire_effectif": {
                            "type": "object",
                            "description": "Current effective salary data.",
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
                            "additionalProperties": false,
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
                    "additionalProperties": false,
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
            "additionalProperties": false
        }
    }
}]
