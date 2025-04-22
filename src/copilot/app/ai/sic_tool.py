from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

client = OpenAI()

branches = [
    'TOTAL',
    'SECTEUR PRIMAIRE',
    'SECTEUR SECONDAIRE',
    'Industries extractives',
    'Industrie manufacturière',
    'Industries alimentaires et du tabac',
    'Industries du textile et de l’habillement',
    'Industries du bois et du papier\xa0; imprimerie',
    'Cokéfaction, raffinage et industrie chimique',
    'Industrie pharmaceutique',
    'Industries du caoutchouc et du plastique',
    'Fabrication de produits métalliques',
    'Fabrication de produits électroniques; horlogerie',
    'Fabrication d’équipements électriques',
    'Fabrication de machines et équipements n.c.a',
    'Fabrication de matériels de transport',
    'Autres industries manufacturières; rép. et inst.',
    'Production et distribution d’énergie',
    'Production et distr. d’eau; gestion des déchets',
    'Construction',
    'Construction de bâtiments et génie civil',
    'Travaux de construction spécialisés',
    'SECTEUR TERTIAIRE',
    "Commerce; réparation d'automobiles et de motocycles",
    'Commerce et rép. d\\’automobiles et de motocycles',
    'Commerce de gros',
    'Commerce de détail',
    'Transport et entreposage',
    'Transports terrestres et transport par conduites',
    'Transports par eau, transports aériens',
    'Entreposage et services auxiliaires des transports',
    'Activités de poste et de courrier',
    'Hébergement et restauration',
    'Hébergement',
    'Restauration',
    'Information et communication',
    'Édition, audiovisuel et diffusion',
    'Télécommunications',
    'Activités informatiques et services d’information',
    "Activités financières et d'assurance",
    'Activités des services financiers',
    'Assurance',
    'Activités aux. de services financiers et d’assurance',
    'Activités immobilières',
    'Activités spécialisées, scientifiques et techniques',
    'Activités juridiques et comptables',
    'Activités des sièges sociaux\xa0; conseil de gestion',
    'Activités d’architecture et d’ingénierie',
    'Recherche-développement scientifique',
    'Autres activités spécialisées, scient. et techn.',
    'Activités de services administratifs et de soutien',
    'Activités de services administratifs (sans 78)',
    "Activités liées à l'emploi",
    'Administration publique',
    'Enseignement',
    'Santé humaine et action sociale',
    'Activités pour la santé humaine',
    'Hébergement médico-social et social',
    'Action sociale sans hébergement',
    'Arts, spectacles et activités récréatives',
    'Autres activités de services'
 ]

description = """
    Calcul le salaire exigible d'une personne benéficiant d'une rente assurance invalidité. les informations sont fourni selon le format suivant:
    
    Information personnelle:
            Sexe: ____
        Information avant l'atteinte à la santé:
            année de réference: 2022
            Branche: ____
            niveau de compétence: __
            Taux d’activité : ___%
            Revenu sans invalidité effectif ____ : CHF ________
        Information après l'atteinte à la santé:
            année de réference: 2022
            Branche: ______
            niveau de compétence: __
            Diminution du taux d’activité : __%
            Revenu effectif ____: CHF ______
            abattement: __%
        Date de l’exigibilité : __.__.____

    les _ sont remplacé par les informations.
"""

tools = [{
    "type": "function",
    "function": {
        "name": "get_invalidite",
        "description": description,
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
                            "description": "Déduction du taux supplémentaire, applicable uniquement si la date d'exigibilité est inférieur à 2024."
                        },
                        "diminution": {
                            "type": "number",
                            "description": "Réduction du taux d'activité après l'atteinte à la santé en %. Peut-être déduis en calculant taux avant atteinte à la santé - taux après atteinte à la santé."
                        },
                        "ess": {
                            "type": "number",
                            "description": "Correspond à l'année d'exigibilié du cas."
                        },
                        "ex": {
                            "type": "object",
                            "description": "Les données nécessaires au calcul du salaire statistique exigible (après l'atteinte à la santé).",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "L'année de référence, toujours égal à 2022."
                                },
                                "branche": {
                                    "type": "string",
                                    "enum": branches,
                                    "description": "La branche économique."
                                },
                                "niveau_comp": {
                                    "type": "number",
                                    "enum": [
                                        1,
                                        2,
                                        3,
                                        4
                                    ],
                                    "description": "Le niveau de compétence. Le niveau de compétence est décris comme suis: 4 = Tâches qui exigent une capacité à résoudre des problèmes complexes et à prendre des décisions fondées sur un vaste ensemble de connaissances théoriques et factuelles dans un domaine spécialisé. 3 = Tâches pratiques complexes nécessitant un vaste ensemble de connaissances dans un domaine spécialisé. 2 = Tâches pratiques telles que la vente/ les soins/ le traitement de données et les tâches administratives/ l'utilisation de machines et d'appareils électroniques/ les services de sécurité/ la conduite de véhicules. 1 = Tâches physiques ou manuelles simples."
                                }
                            },
                            "additionalProperties": False,
                            "required": [
                                "année",
                                "branche",
                                "niveau_comp"
                            ]
                        },
                        "horaire": {
                            "type": "number",
                            "description": "Taux d’activité en %."
                        },
                        "salaire_as": {
                            "type": "object",
                            "description": "Le salaire du demandeur avant l'atteinte à la santé. (peut être nul)",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "La dernière année où le salaire a été perçu."
                                },
                                "salaire": {
                                    "type": "number",
                                    "description": "le revenu annuel."
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
                            "description": "Les données nécessaires au calcul du salaire statistique (avant l'atteinte à la santé).",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "L'année de référence, toujours égal à 2022."
                                },
                                "branche": {
                                    "type": "string",
                                    "enum": branches,
                                    "description": "La branche économique."
                                },
                                "niveau_comp": {
                                    "type": "number",
                                    "enum": [
                                        1,
                                        2,
                                        3,
                                        4
                                    ],
                                    "description": "Le niveau de compétence. Le niveau de compétence est décris comme suis: 4 = Tâches qui exigent une capacité à résoudre des problèmes complexes et à prendre des décisions fondées sur un vaste ensemble de connaissances théoriques et factuelles dans un domaine spécialisé. 3 = Tâches pratiques complexes nécessitant un vaste ensemble de connaissances dans un domaine spécialisé. 2 = Tâches pratiques telles que la vente/ les soins/ le traitement de données et les tâches administratives/ l'utilisation de machines et d'appareils électroniques/ les services de sécurité/ la conduite de véhicules. 1 = Tâches physiques ou manuelles simples."
                                }
                            },
                            "additionalProperties": False,
                            "required": [
                                "année",
                                "branche",
                                "niveau_comp"
                            ]
                        },
                        "salaire_effectif": {
                            "type": "object",
                            "description": "Le salaire du demandeur après l'atteinte à la santé. (peut être nul)",
                            "properties": {
                                "année": {
                                    "type": "number",
                                    "description": "L'année où le salaire est perçu."
                                },
                                "salaire": {
                                    "type": "number",
                                    "description": "le revenu annuel."
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
                            "enum": [
                                "homme",
                                "femme",
                                "26 al. 6 RAI"
                            ],
                            "description": "le sexe permet de déterminé le tableau de référence pour le calcul du salaire, dans certain cas il peut prendre la valeur '26 al. 6 RAI' en référence à un cas spécifique ou le sexe n'est pas pris en compte."
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

calc_ai_prompt = """
    <context>
        L'utilisateur intéragit avec le copilote en lui soumettant des cas pour lesquels il doit prendre la décision d'octroyer ou non des rente assurances et calculer leur montant. Les informations données peuvent parfoit être incomplêtes. Il est nécessaire de guider l'utilisateur afin d'obtenir toutes les informations nécessaire à la prise de décision afin d'ensuite reformuler la question sous la forme d'une description détaillée, contenant toute les informations requises.
    </context>

    <objectif>
        Obtenir toutes les informations nécessaires au calcul de la rente assurance invalidité puis écrire une déscription du cas complète et précise.
    </objectif>

    <instructions>
        <instruction>Étant donné la déscription donner par l'utilisateur, vérifiez si il manque des informations en vous référant au <data></instruction>
        <instruction>Si il manque des informations demandez à l'utilisateur de compléter les informations manquante.</instruction>
        <instruction>Si vous avez toute les informations, rédiger une déscription détaillée du cas à traiter en incluant toute les informations pertinentes.</instruction>
        <instruction>Si il manque des informations demandez à l'utilisateur de compléter les informations manquante.</instruction>
        <instruction>Les informations concernant sainv, ex, horaire, diminution et abattement peuvent être nul, en cas de doute demandez une confirmation à l'utilisateur.</instruction>
        <instruction>Si elles sont nuls atribuez la valeur de 0 ou de "" (selon le type de valeur).</instruction>
        <instruction>Le niveau de compétence est décris comme suis: 4 = Tâches qui exigent une capacité à résoudre des problèmes complexes et à prendre des décisions fondées sur un vaste ensemble de connaissances théoriques et factuelles dans un domaine spécialisé. 3 = Tâches pratiques complexes nécessitant un vaste ensemble de connaissances dans un domaine spécialisé. 2 = Tâches pratiques telles que la vente/ les soins/ le traitement de données et les tâches administratives/ l'utilisation de machines et d'appareils électroniques/ les services de sécurité/ la conduite de véhicules. 1 = Tâches physiques ou manuelles simples.</instruction>
        <instruction>La branche économique doit obligatoirement être dans <branche-liste>.</instruction>
        <instruction>Si l'utilisateur fourni 2 taux d'activité, un avant et un après l'atteinte à la santé, la diminution prend comme valeur la différence entre les 2.</instruction>
        <instruction>Si la date d'éxigibilité est postérieur au 31.12.2023, l'abattement prend obligatoirement 0 comme valeur.</instruction>
        <instruction>Une fois que vous avez toutes les informations confirmez avec l'utilisateur que tout est correcte.</instruction>
        <instruction>Corrigez les erreurs si besoin puis redemendez une confirmation.</instruction>
        <instruction>Une fois que l'utilisateur confirme, génerez une réponse dont le contenu est strictement limité à <format_de_réponse>.</instruction>
        <instruction>Aucun texte mise à part celui de la reformulation des informations ne doit être généré.</instruction>
    </instructions>

    <data>
        beneficiary = {
            "ess": int,                             # Correspond à l'année d'exigibilié du cas.
            "sexe": str,                            # le sexe permet de déterminé le tableau de référence pour le calcul du salaire, dans certain cas il peut prendre la valeur "26 al. 6 RAI" en référence à un cas spécifique ou le sexe n'est pas pris en compte.
            "salaire_as": {                         # Le salaire du demandeur avant l'atteinte à la santé. (peut être nul)
                "salaire": double,                      # le revenu annuel.
                "année": int                            # La dernière année où le salaire a été perçu. 
            },
            "sainv": {                              # Les données nécessaires au calcul du salaire statistique (avant l'atteinte à la santé).
                "année": int = 2022,                    # L'année de référence, toujours égal à 2022.
                "niveau_comp": int in range(1,5),       # Le niveau de compétence.
                "branche": str,                         # La branche économique.
            },                 
            "ex": {                                 # Les données nécessaires au calcul du salaire statistique exigible (après l'atteinte à la santé).
                "année": int = 2022,                    # L'année de référence, toujours égal à 2022.
                "niveau_comp": int in range(1,5),       # Le niveau de compétence.
                "branche": str,                         # La branche économique.
            },                  
            "salaire_effectif": {                   # Le salaire du demandeur après l'atteinte à la santé. (peut être nul)
                "salaire": double,                      # le revenu annuel.
                "année": int                            # L'année où le salaire est perçu. 
            },
            "horaire": int in range(0,101),         # Taux d’activité en %.
            "diminution": int in range(0,101),      # Réduction du taux d'activité après l'atteinte à la santé en %.
            "abattement": int in range(0,101),      # Déduction du taux supplémentaire, applicable uniquement si la date d'exigibilité est inférieur à 2024.
        }
    </data>

    <format_de_réponse>
        Information personnelle:
            Sexe: ____
        Information avant l'atteinte à la santé:
            année de réference: 2022
            Branche: ____
            niveau de compétence: __
            Taux d’activité : ___%
            Revenu sans invalidité effectif ____ : CHF ________
        Information après l'atteinte à la santé:
            année de réference: 2022
            Branche: ______
            niveau de compétence: __
            Diminution du taux d’activité : __%
            Revenu effectif ____: CHF ______
            abattement: __%
        Date de l’exigibilité : __.__.____
    </format_de_réponse>

    <exemples>
        User:
            Activité avant atteinte à la santé : Ouvrier de la construction qualifié (CFC)
            Taux d’activité : 100% / Revenu sans invalidité effectif 2021 : CHF 90'000.00
            Activité exigible avec invalidité : Activité légère non qualifiée dans la production ou les services
            Taux d’activité : 100%
            Date de l’exigibilité : 01.07.2022
            
        Assistant:
            Information personnelle:
                    Sexe: homme
            Information avant l'atteinte à la santé:
                année de réference: 2022
                Branche: Construction
                niveau de compétence: 2
                Taux d’activité : 100%
                Revenu sans invalidité effectif 2021 : CHF 90'000.00
            Information après l'atteinte à la santé:
                année de réference: 2022
                Branche: _____
                niveau de compétence: 1
                Diminution du taux d’activité : 0%
                Revenu effectif 2022: CHF _____
                abattement: __%
            Date de l’exigibilité : 01.07.2022
            
            J'ai besoin de quelques précision pour compléter les informations fournies: qu'elle est la branche à prendre en compte pour le calcul du revenu exigible selon ESS? la personne avait-t-elle un revenu effectif au moment de la demande ? Y a-t-il d'autres d'éduction du taux / abattement à prendre en compte ?
        
        User:
            La branche à prendre en compte est la branche TOTAL. Pas de revenu effectif et pas de déduction supplémentaire.

        Assistant:
            Information personnelle:
                    Sexe: homme
            Information avant l'atteinte à la santé:
                année de réference: 2022
                Branche: Construction
                niveau de compétence: 2
                Taux d’activité : 100%
                Revenu sans invalidité effectif 2021 : CHF 90'000.00
            Information après l'atteinte à la santé:
                année de réference: 2022
                Branche: TOTAL
                niveau de compétence: 1
                Diminution du taux d’activité : 0%
                Revenu effectif 0: CHF 0.00
                abattement: 0
            Date de l’exigibilité : 01.07.2022

            Si les informations sont correcte je vais procéder au calcul du salaire exigible.

            
        User:
            Les informations sont correctes.

        Assistant:
            Information personnelle:
                    Sexe: homme
            Information avant l'atteinte à la santé:
                année de réference: 2022
                Branche: Construction
                niveau de compétence: 2
                Taux d’activité : 100%
                Revenu sans invalidité effectif 2021 : CHF 90'000.00
            Information après l'atteinte à la santé:
                année de réference: 2022
                Branche: TOTAL
                niveau de compétence: 1
                Diminution du taux d’activité : 0%
                Revenu effectif 0: CHF 0.00
                abattement: 0
            Date de l’exigibilité : 01.07.2022
    </exemples>

    <branche-liste> 
        '01-96': 'TOTAL',
        '01-03': 'SECTEUR PRIMAIRE',
        '05-43': 'SECTEUR SECONDAIRE',
        '05-9': 'Industries extractives',
        '10-33': 'Industrie manufacturière',
        '10-12': 'Industries alimentaires et du tabac',
        '13-15': 'Industries du textile et de l’habillement',
        '16-18': 'Industries du bois et du papier\xa0; imprimerie',
        '19-20': 'Cokéfaction, raffinage et industrie chimique',
        '21': 'Industrie pharmaceutique',
        '22-23': 'Industries du caoutchouc et du plastique',
        '24-25': 'Fabrication de produits métalliques',
        '26': 'Fabrication de produits électroniques; horlogerie',
        '27': 'Fabrication d’équipements électriques',
        '28': 'Fabrication de machines et équipements n.c.a',
        '29-30': 'Fabrication de matériels de transport',
        '31-33': 'Autres industries manufacturières; rép. et inst.',
        '35': 'Production et distribution d’énergie',
        '36-39': 'Production et distr. d’eau; gestion des déchets',
        '41-43': 'Construction',
        '41-42': 'Construction de bâtiments et génie civil',
        '43': 'Travaux de construction spécialisés',
        '45-96': 'SECTEUR TERTIAIRE',
        '45-47': "Commerce; réparation d'automobiles et de motocycles",
        '45': 'Commerce et rép. d\\’automobiles et de motocycles',
        '46': 'Commerce de gros',
        '47': 'Commerce de détail',
        '49-53': 'Transport et entreposage',
        '49': 'Transports terrestres et transport par conduites',
        '50-51': 'Transports par eau, transports aériens',
        '52': 'Entreposage et services auxiliaires des transports',
        '53': 'Activités de poste et de courrier',
        '55-56': 'Hébergement et restauration',
        '55': 'Hébergement',
        '56': 'Restauration',
        '58-63': 'Information et communication',
        '58-60': 'Édition, audiovisuel et diffusion',
        '61': 'Télécommunications',
        '62-63': 'Activités informatiques et services d’information',
        '64-66': "Activités financières et d'assurance",
        '64': 'Activités des services financiers',
        '65': 'Assurance',
        '66': 'Activités aux. de services financiers et d’assurance',
        '68': 'Activités immobilières',
        '69-75': 'Activités spécialisées, scientifiques et techniques',
        '69': 'Activités juridiques et comptables',
        '70': 'Activités des sièges sociaux\xa0; conseil de gestion',
        '71': 'Activités d’architecture et d’ingénierie',
        '72': 'Recherche-développement scientifique',
        '73-75': 'Autres activités spécialisées, scient. et techn.',
        '77-82': 'Activités de services administratifs et de soutien',
        '77+79-82': 'Activités de services administratifs (sans 78)',
        '78': "Activités liées à l'emploi",
        '84': 'Administration publique',
        '85': 'Enseignement',
        '86-88': 'Santé humaine et action sociale',
        '86': 'Activités pour la santé humaine',
        '87': 'Hébergement médico-social et social',
        '88': 'Action sociale sans hébergement',
        '90-93': 'Arts, spectacles et activités récréatives',
        '94-96': 'Autres activités de services'
    </branche-liste>
"""
