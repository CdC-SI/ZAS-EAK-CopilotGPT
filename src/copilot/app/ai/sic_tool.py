from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

client = OpenAI()

tools = [{
    "type": "function",
    "function": {
        "name": "mise_en_parallele_des_revenus",
        "description": "Defines the properties of a beneficiary in a social assistance context",
        "strict": True,
        "parameters": {
            "type": "object",
            "required": [
                "sexe",
                "branche",
                "niveau_comp",
                "salaire_ofs",
                "ess",
                "salaire_effectif",
                "horaire",
                "diminution",
                "salaire_as",
                "abattement"  
            ],
            "properties": {
                "sexe": {
                    "type": "string",
                    "description": "Le sexe du demandeur. Valeurs acceptées : ['homme', 'femme', '26 al. 6 RAI']"
                },
                "branche": {
                    "type": "string",
                    "description": "La branche économique. ex: (05-96)"
                },
                "niveau_comp": {
                    "type": "integer",
                    "description": "Le niveau de compétence."
                },
                "salaire_ofs": {
                    "type": "object",
                    "required": [
                        "année",
                        "salaire"
                    ],
                    "properties": {
                        "année": {
                            "type": "integer",
                            "description": "Année de référence."
                        },
                        "salaire": {
                            "type": "number",
                            "description": "Salaire OFS."
                        }
                    },
                    "additionalProperties": False
                },
                "ess": {
                    "type": "integer",
                    "description": "Année d'exigibilité."
                },
                "salaire_effectif": {
                    "type": "object",
                    "required": [
                        "salaire",
                        "année"
                    ],
                    "properties": {
                        "salaire": {
                            "type": "integer",
                            "description": "Salaire effectif. ne pas confondre avec revenu sans activité effectif"
                        },
                        "année": {
                            "type": "number",
                            "description": "Année correspondante."
                        }
                    },
                    "additionalProperties": False
                },
                "horaire": {
                    "type": "integer",
                    "description": "Taux d'activité. Valeur entre 0-100."
                },
                "diminution": {
                    "type": "integer",
                    "description": "Réduction du taux d'activité. Valeur entre 0-100."
                },
                "salaire_as": {
                    "type": "object",
                    "required": [
                        "salaire",
                        "année"
                    ],
                    "properties": {
                        "salaire": {
                            "type": "number",
                            "description": "Salaire avant l'atteinte à la santé ou revenu sans activité effectif."
                        },
                        "année": {
                            "type": "integer",
                            "description": "Année correspondante."
                        }
                    },
                    "additionalProperties": False
                },
                "abattement": {
                    "type": "number"
                }
            },
            "additionalProperties": False
        }
    }
}]
