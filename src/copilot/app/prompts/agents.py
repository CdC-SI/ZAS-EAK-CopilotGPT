INTENT_DETECTION_PROMPT_DE = """# Aufgabe
Ihre Aufgabe besteht darin:
- die Absicht des Nutzers auf der Grundlage der gestellten Frage und des Gesprächsverlaufs zu ermitteln
- auf der Grundlage der Fragestellung und der verfügbaren Themen zu bestimmen, welche Themen für die Suche nach Dokumenten ausgewählt werden sollen.
- den geeigneten Agenten auf der Grundlage der Absicht und des Themas (der Themen) auswählen.
- entscheiden, ob zusätzliche Informationen oder Klarstellungen erforderlich sind, um die Absicht des Nutzers genau zu identifizieren. WICHTIG: Sehen Sie sich die verfügbaren Dokumente UND die verfügbaren Themen an, um festzustellen, ob eine Klärung erforderlich ist oder nicht. Wenn ein Dokument oder ein Thema die Frage beantworten kann, stellen Sie keine Folgefrage.

# Wichtige Anmerkungen
Die Absicht des Nutzers kann allgemein oder spezifisch sein.
Zum Beispiel eine Frage zu Themen im Zusammenhang mit AHV/IV, Kindergeld, Erwerbsausfallentschädigung, Mutterschaftsgeld usw. stellen.
Zum Beispiel eine sehr spezifische Frage zu einer Berechnung stellen, die sich auf die persönliche Situation des Nutzers bezieht (Alter, Einkommen usw.).
Wenn Sie eine Folgefrage stellen müssen, stellen Sie sie AUF DEUTSCH!!!
WICHTIG: Stellen Sie nur eine Anschlussfrage, wenn die Frage sehr vage formuliert ist ODER wenn die Frage mithilfe der verfügbaren Dokumente/Themen nicht (oder nur teilweise) beantwortet werden kann. Wenn sich die Frage auf das Thema AHV/IV im Allgemeinen bezieht, stellen Sie keine Anschlussfrage.

## Agenten
- RAG_AGENT: Beantwortet allgemeine Fragen zu:
    - Alters- und Hinterlassenenversicherung (AHV)
    - Invalidenversicherung (IV)
    - Ergänzungsleistungen (EL)
    - Überbrückungsleistungen (ÜL)
    - Leistungen aus dem System der Erwerbsausfallentschädigungen (EO), Mutterschaftsentschädigung (MSE), Entschädigung des andern Elternteils (Vater oder Ehefrau der Mutter) (EAE), Betreuungsentschädigung (BUE), Adoptionsentschädigung (AdopE)
    - Familienzulagen (FZ)
    - Weitere Sozialversicherungen
    - Internationales
    - Beiträge, Leistungen, Anspruch usw.
- PENSION_AGENT: Beantwortet nur die spezifischen mathematischen Berechnungen für den Ruhestand, insbesondere:
    - die Berechnung des Kürzungssatzes und des Rentenzuschlags für Frauen der Übergangsgeneration (1961-1969)
    - die Berechnung der geschätzten Altersrente
    - Berechnung des Referenzalters (Alter, in dem eine Person ihre Altersrente erhält).
- FAK_EAK_AGENT: Beantwortet Fragen zu Kindergeld, insbesondere:
    - die Bestimmung (Berechnung), welcher Elternteil das Kindergeld erhält.
- APG_AGENT: Beantwortet Fragen zur Erwerbsausfallentschädigung.
    - die Bestimmung (Berechnung) des EO-Taggeldes aufgrund des Dienstes (Militärdienst, Zivildienst usw.)
    - die Bestimmung (Berechnung) des Taggelds der MSE (Mutterschaftsentschädigung)

# Format der Antwort
IntentDetection(
    intent: str, # die Absicht des Nutzers in einem verständlichen Satz
    tags: List[str] = None, # das/die identifizierte(n) Thema(e) der Frage
    agent: str = None, # der Name des entsprechenden Agenten, der die Frage beantwortet.
    followup_required: bool = False, # True, wenn zusätzliche Informationen erforderlich sind, um die Absicht des Nutzers genau zu identifizieren, False andernfalls.
    followup_question: str = None, # Folgefrage, um zusätzliche Informationen zu erhalten, wenn followup_required True ist.
)
Wenn die Absicht, die Themen, der passende Agent nicht bestimmt werden können, können Sie für diese Werte „None“ angeben und „followup_required“ und „followup_question“ ausfüllen.

# Beispiele für die Auswahl des Agenten
Für allgemeine Fragen zur AHV/IV -> RAG_AGENT
Wie bestimme ich meinen Anspruch auf Ergänzungsleistungen? -> RAG_AGENT
Welche Voraussetzungen muss ich erfüllen, um eine IV-Rente zu erhalten? -> RAG_AGENT
Wann werden Ergänzungsleistungen gezahlt? -> RAG_AGENT
Wann entsteht der Anspruch auf eine Altersrente? -> RAG_AGENT
Was ändert sich mit AHV 21? -> RAG_AGENT
Was bedeutet das flexible Rentenalter? -> RAG_AGENT

Für sehr spezifische (individualisierte) Fragen zu Berechnungen von Kürzungssätzen und Rentenzuschlägen im Zusammenhang mit dem Eintritt in den Ruhestand und dem Bezug von Altersrenten -> PENSION_AGENT
Ich bin am 1962.31.12 geboren, möchte am 01.01.2025 in Rente gehen und mein Jahreseinkommen beträgt ca. 55'000 CHF. Wie hoch ist mein Kürzungssatz? -> PENSION_AGENT
Wie hoch ist mein Kürzungssatz, wenn ich am 1965-11-07 geboren bin, am 2026-04-15 in Rente gehen möchte und mein Jahreseinkommen 76200 beträgt? -> PENSION_AGENT
Hier sind meine Informationen: Geburtsdatum 03.01.1968 und ich gehe 2027 in Rente. Ich verdiene etwa 90000 CHF pro Jahr. Kann ich einen Zuschlag oder einen Kürzungssatz erhalten? -> PENSION_AGENT
Für sehr spezifische (individualisierte) Fragen zur Berechnung des Referenzalters für Frauen der Übergangsgeneration (1961-1969) -> PENSION_AGENT
Wenn ich eine Frau bin, die 1960 geboren wurde, wie hoch ist mein Referenzalter? -> PENSION_AGENT
Ich bin eine 1961 geborene Frau, was ist mein Referenzalter? -> PENSION_AGENT
Ich bin am 01.01.1962 geboren, wie hoch ist mein Referenzalter? -> PENSION_AGENT

Bei Fragen zum Kindergeld -> FAK_EAK_AGENT
Welche Arten von Kindergeld werden gezahlt? -> FAK_EAK_AGENT
Wie hoch ist das Kindergeld? -> FAK_EAK_AGENT
Werden die Zulagen nach dem Wohnkanton oder dem Arbeitskanton bestimmt? -> FAK_EAK_AGENT
Wer hat Anspruch auf Kinderzulagen? -> FAK_EAK_AGENT
Welcher Elternteil erhält die Kinderzulagen? -> FAK_EAK_AGENT
Wie können Sie Ihren Anspruch auf Kindergeld bei der Familienausgleichskasse der Eidgenössischen Ausgleichskasse (FAK-EAK) geltend machen? -> FAK_EAK_AGENT
Wie können Sie einen bestehenden Anspruch auf Ausbildungszulagen verlängern? -> FAK_EAK_AGENT
Wie werden die Familienzulagen der Familienausgleichskasse der Eidgenössischen Ausgleichskasse ausbezahlt? -> FAK_EAK_AGENT

# Gesprächsverlaufs
{conversational_memory}

#Dokumente zur Verfügung
{Dokumente}

# Themen zur Verfügung
{tags}

# Frage
{query}"""


INTENT_DETECTION_PROMPT_FR = """# Tâche
Votre tâche consiste à:
- déterminer l'intention de l'utilisateur en fonction de la question posée et de l'historique de conversation
- déterminer quel(s) thème(s) sélectionner pour la recherche de documents basé sur la question posée et sur les thèmes à disposition
- déterminer si des clarifications ou des informations supplémentaires sont nécessaires pour identifier l'intention de l'utilisateur de manière précise. IMPORTANT: regardez les documents à disposition ET les thèmes à disposition pour déterminer si des clarifications sont nécessaires ou non. Si un document ou un thème peut répondre à la question, ne posez pas de question de suivi.

# Notes importantes
L'intention de l'utilisateur peut être générale ou spécifique.
Par exemple, poser une question sur les thèmes liés à l'AVS/AI, aux allocations familiales, aux allocations pour perte de gain, aux allocations de maternité, etc.
Par exemple, poser une question très spécifique à un calcul lié à la situation personnelle de l'utilisateur (âge, revenu, etc.).
Si vous devez poser une question de suivi, posez la EN FRANCAIS !!!
IMPORTANT: Posez seulement une question de suivi si la question est formulée de manière très vague OU si les documents/thèmes à disposition ne permettent pas de répondre à la question (ou seulement de manière partielle). Si la question porte sur le thème de l'AVS/AI de manière générale, ne posez pas de question de suivi.

# Format de réponse
IntentDetection(
    intent: str, # l'intention de l'utilisateur en une phrase couerte
    tags: List[str] = None, # le(s) thème(s) identifié de la question
    followup_required: bool = False, # True si des informations supplémentaires sont nécessaires pour identifier l'intention de l'utilisateur de manière précise, False sinon.
    followup_question: str = None, # Question de suivi pour obtenir des informations supplémentaires si followup_required est True.
)
Si l'intention ou les thèmes appropriés ne peuvent être déterminés, vous pouvez spécifier "None" pour ces valeurs et remplir "followup_required" et "followup_question".

# Historique de conversation
{conversational_memory}

# Documents à disposition
{documents}

# Thèmes à disposition
{tags}

# Question
{query}"""


INTENT_DETECTION_PROMPT_IT = """# Compito
Il vostro compito è quello di:
- determinare l'intenzione dell'utente in base alla domanda posta e alla cronologia della conversazione
- determinare quale/i tema/i selezionare per la ricerca di documenti in base alla domanda posta e ai temi disponibili
- selezionare l'agente appropriato in base all'intenzione e ai temi disponibili
- determinare se sono necessari chiarimenti o informazioni aggiuntive per identificare con precisione l'intenzione dell'utente. IMPORTANTE: esaminare i documenti disponibili E i temi disponibili per determinare se sono necessari o meno chiarimenti. Se un documento o un tema è in grado di rispondere alla domanda, non porre una domanda successiva.

# Note importanti
L'intenzione dell'utente può essere generale o specifica.
Ad esempio, porre una domanda su argomenti relativi all'AVS/AI, agli assegni familiari, alle indennità di perdita di guadagno, agli assegni di maternità, ecc. potrebbe essere molto specifico.
Ad esempio, porre una domanda molto specifica su un calcolo legato alla situazione personale dell'utente (età, reddito, ecc.).
Se dovete fare una domanda di approfondimento, fatela IN ITALIANO!
IMPORTANTE: porre una domanda di follow-up solo se la domanda è formulata in modo molto vago O se i documenti/temi disponibili non consentono di rispondere alla domanda (o solo parzialmente). Se la domanda riguarda l'AVS/AI in generale, non porre una domanda di approfondimento.

- RAG_AGENT: risponde a domande generali su:
    - Assicurazione vecchiaia e superstiti (AVS)
    - Assicurazione per l'invalidità (AI)
    - Prestazioni complementari (PC)
    - Prestazioni transitorie per i disoccupati anziani (PT)
    - Prestazioni dell'IPG (IPG): Indennità per chi presta servizio, Indennità in caso di maternità, Indennità per l'altro genitore (per il padre o la moglie della madre), Indennità di assistenza, Indennità di adozione
    - Assegni familiari (AF)
    - Altri tipi di assicurazione sociale
    - Internazionale
    - Contributi, prestazioni, diritti, ecc.
- PENSION_AGENT: risponde solo ai calcoli matematici specifici per la pensione, in particolare:
    - calcolo del tasso di riduzione e del supplemento di pensione per le donne della generazione di transizione (1961-1969)
    - calcolo della pensione stimata
    - calcolo dell'età di riferimento (l'età in cui una persona riceve la pensione di vecchiaia).
- FAK_EAK_AGENT: risponde a domande sugli assegni familiari, in particolare:
    - determinare (calcolare) quale genitore riceve gli assegni familiari
- APG_AGENT: risponde alle domande sulle indennità di perdita di guadagno
    - determinazione (calcolo) delle prestazioni giornaliere APG in base al servizio (servizio militare, servizio civile, ecc.)
    - determinare (calcolare) le indennità giornaliere (indennità di maternità)

# Formato della risposta
IntentDetection(
    intent: str, # l'intento dell'utente in una frase
    tags: List[str] = None, # i temi identificati della domanda
    agent: str = None, # il nome dell'agente appropriato per rispondere alla domanda.
    followup_required: bool = False, # True se sono necessarie informazioni aggiuntive per identificare con precisione l'intento dell'utente, False altrimenti.
    followup_question: str = None, # domanda successiva per ottenere informazioni aggiuntive se followup_required è True.
)
Se non è possibile determinare l'intenzione, i temi e l'agente appropriato, è possibile specificare None per questi valori e compilare “followup_required” e “followup_question”.

# Esempi di selezione degli agenti
Per domande generali sull'AVS/AI -> RAG_AGENT
Come si determina il diritto alle prestazioni complementari? -> RAG_AGENT
Quali sono le condizioni per ricevere una rendita AI? -> RAG_AGENT
Quando vengono versate le prestazioni complementari? -> RAG_AGENT
Quando nasce il diritto alla pensione di vecchiaia? -> RAG_AGENT
Cosa cambia con l'AVS 21? -> RAG_AGENT
Cosa significa l'età pensionabile flessibile? -> RAG_AGENT

Per domande molto specifiche (personalizzate) relative al calcolo dei tassi di riduzione e dei supplementi di pensione legati al pensionamento e al percepimento di pensioni di vecchiaia -> PENSION_AGENT
Sono nato il 31.12.1962, voglio andare in pensione il 01.01.2025 e il mio reddito annuo è di circa 55.000 franchi. Qual è il mio tasso di riduzione? -> PENSION_AGENT
Qual è il mio tasso di riduzione se sono nato il 1965-11-07, voglio andare in pensione il 2026-04-15 e il mio reddito annuo è di CHF 76200? -> PENSION_AGENT
Ecco le mie informazioni: sono nato il 03.01.1968 e andrò in pensione nel 2027. Guadagno circa 90.000 franchi all'anno. Posso beneficiare di un'integrazione o di una riduzione? -> PENSION_AGENT
Per domande molto specifiche (personalizzate) sul calcolo dell'età di riferimento per le donne della generazione di transizione (1961-1969) -> PENSION_AGENT
Se sono una donna nata nel 1960, qual è la mia età di riferimento? -> PENSION_AGENT
Se sono una donna nata nel 1961, qual è la mia età di riferimento? -> PENSION_AGENT
Sono nato il 01.01.1962, qual è la mia età di riferimento? -> PENSION_AGENT

Per domande sugli assegni familiari -> FAK_EAK_AGENT
Quali tipi di assegni familiari vengono erogati? -> FAK_EAK_AGENT
A quanto ammontano gli assegni familiari? -> FAK_EAK_AGENT
L'assegno viene pagato in base al cantone di residenza o al cantone di occupazione? -> FAK_EAK_AGENT
Chi ha diritto agli assegni familiari? -> FAK_EAK_AGENT
Quale genitore riceve gli assegni familiari? -> FAK_EAK_AGENT
Come richiedere gli assegni familiari alla Caisse d'allocations familiales de la Caisse fédérale de compensation (CAF-CFC)? -> FAK_EAK_AGENT
Come si può estendere un diritto esistente agli assegni di formazione? -> FAK_EAK_AGENT
Come vengono pagati gli assegni familiari dalla Cassa per gli assegni familiari della Cassa federale di compensazione? -> FAK_EAK_AGENT

# Storia della conversazione
{conversational_memory}

# Documenti disponibili
{documents}

# Temi disponibili
{tags}

# Domanda
{query}"""


SOURCE_SELECTION_PROMPT_DE = """# Aufgabe
"""


SOURCE_SELECTION_PROMPT_FR = """# Tâche
Votre tâche consiste à sélectionner la source de données appropriée pour répondre à la question de l'utilisateur. Vous devez baser votre décision en fonction de:
- la question de l'utilisateur
- l'intention de l'utilisateur
- du thème
- de l'historique de conversation
- les sources de données disponibles

# Notes importantes
- Si un utilisateur a téléchargé un document, vous le trouvez dans les sources de données disponibles.
- La conversation peut commencer avec des questions générales sur l'AVS/AI, puis se concentrer sur un document particulier que l'utilisateur a téléchargé, puis revenir à des questions générales.
- La conversation peut se concentrer uniquement sur un document particulier que l'utilisateur a téléchargé.
- La conversation peut se concentrer uniquement sur des questions générales sur l'AVS/AI.
- Si plusieurs sources pourraient répondre à la question, sélectionnez les toutes.
- Si vous n'êtes pas sûr de la source à sélectionner, vous pouvez demander des clarifications à l'utilisateur en spécifiant "followup_required: True" dans l'objet de réponse.
- IMPORTANT: Consultez TOUJOURS la description des sources de données disponibles pour vous aider à sélectionner la source appropriée.
- IMPORTANT: Vous ne pouvez sélectionner des sources UNIQUEMENT parmi les sources de données disponibles.

# Format de réponse
SourceSelection(
    selected_sources: List[str] # la (ou les) source(s) de données sélectionnée (e.g. ["<file_upload_name.pdf>"], ["ahv-iv.ch"], ["eak.admin.ch", "AHV Lernbaustein 2024"], ["Praxisleitfaden FAK-EAK"], ["AKIS Online Hilfe"], etc.)
    followup_required: bool = False # True, si des informations supplémentaires sont nécessaires pour sélectionner une source, False sinon.
    followup_question: str = None # Question de suivi pour obtenir des informations supplémentaires si followup_required est True.
)

# Exemples
Si un utilisateur a téléchargé un document et semble vouloir interroger le contenu de ce document, vous devez sélectionner ce document comme source.
Si un utilisateur pose des questions générales (grand public) sur l'AVS/AI, vous pouvez sélectionner "ahv-iv.ch" comme source.
Si un utilisateur pose des questions spécifiques (professionnelles) sur l'AVS/AI, vous pouvez sélectionner "AHV Lernbaustein 2024" comme source.
Si un utilisateur pose des questions spécifiques (professionnelles) sur les procédures des allocations familiales, vous pouvez sélectionner "Praxisleitfaden FAK-EAK" comme source.
Si un utilisateur pose des questions spécifiques à l'Eidgenössische Ausgleichskasse (EAK), vous pouvez sélectionner "eak.admin.ch" comme source.
Si un utilisateur pose des questions très spécifiques sur l'outil AKIS, vous pouvez sélectionner "rag_test_data_tags_lang_org.csv" comme source.

# Question
{query}

# Intention
{intent}

# Thème
{tags}

# Historique de conversation
{conversational_memory}

# Sources de données disponibles
{sources}
"""


SOURCE_SELECTION_PROMPT_IT = """# Compito
"""


AGENT_HANDOFF_PROMPT_DE = """# Aufgabe
"""


AGENT_HANDOFF_PROMPT_FR = """# Tâche
Votre tâche consiste à sélectionner l'agent approprié pour répondre à la question de l'utilisateur. Vous devez baser votre décision en fonction:
- de la question de l'utilisateur
- de l'intention de l'utilisateur
- des thèmes
- de l'historique de conversation
- des agents à disposition

# Format de réponse
AgentHandoff(
    agent: str # le nom de l'agent approprié pour répondre à la question.
)

## Agents à disposition
- RAG_AGENT: répond aux questions générales sur:
    - Assurance Vieillesse (AVS)
    - Assurance Invalidité (AI)
    - Prestations Complémentaires (PC)
    - Prestations Transitoires (PT)
    - Prestations du régime des Assurance Perte de Gain (APG), Assurance Maternité (AMat), Allocations à l'Autre Parent (AAP), Allocations de Prise en Charge (APC), Allocations d'Adoption (AAdop)
    - Allocations familiales (AF)
    - Autres types d'assurance sociale
    - International
    - Cotisations, prestations, droit, etc.
- PENSION_AGENT: répond seulement aux calculs mathématiques spécifiques à la retraite, particulièrement:
    - le calcul du taux de réduction et du supplément de rente pour les femmes de la génération transitoire (1961-1969)
    - le calcul d'estimation de la rente vieillesse
    - le calcul de l'âge de référence (âge auquel une personne perçoit sa rente de vieillesse)
- FAK_EAK_AGENT: répond aux question sur les allocations familiales, particulièrement:
    - la détermination (calcul) de quel parent perçoit les allocations familiales
- APG_AGENT: répond aux questions sur les allocations pour perte de gain
    - la détermination (calcul) de l'indemnité journalière APG en fonction du service (service militaire, service civil, etc.)
    - la détermination (calcul) de l'indemnité journalière AMat (allocations de maternité)

# Exemples
Pour des questions générales relatives à l'AVS/AI -> RAG_AGENT
Comment déterminer mon droit aux prestations complémentaires? -> RAG_AGENT
Quelles sont les conditions pour bénéficier d'une rente AI? -> RAG_AGENT
Quand des prestations complémentaires sont-elles versées ? -> RAG_AGENT
Quand le droit à une rente de vieillesse prend-il naissance ? -> RAG_AGENT
Qu'est-ce qui change avec AVS 21? -> RAG_AGENT
Que signifie l'âge de la retraite flexible ? -> RAG_AGENT

Pour des questions très spécifiques (individualisées) concernant les calculs de taux de réduction et de suppléments de rente liés au départ à la retraite et la perception de rentes vieillesse -> PENSION_AGENT
Je suis née le 1962.31.12, je souhaite prendre ma retraite le 01.01.2025 et mon revenu annuel est d'environ 55'000 CHF. Quel est mon taux de réduction ? -> PENSION_AGENT
Quel sera mon taux de réduction si je suis née le 1965-11-07, je souhaite prendre ma retraite le 2026-04-15 et mon revenu annuel est de 76200 ? -> PENSION_AGENT
Voici mes informations: date de naissance le 03.01.1968 et je pars à la retraite en 2027. Je gagne environ 90000 CHF par an. Puis-je bénéficier d'un supplément ou taux de réduction ? -> PENSION_AGENT
Pour des questions très spécifiques (individualisées) concernant le calcul de l'âge de référence pour les femmes de la génération transitoire (1961-1969) -> PENSION_AGENT
Je suis une femme née en 1960, quel est mon âge de référence ? -> PENSION_AGENT
Je suis née le 01.01.1962, quel sera mon âge de référence ? -> PENSION_AGENT
Je suis une femme, née le 12.02.1960. A quel âge puis-je prendre ma retraite ? -> PENSION_AGENT

À partir de quand puis-je anticiper la perception de ma rente de vieillesse ? -> PENSION_AGENT

Pour des questions sur les allocations familiales -> FAK_EAK_AGENT
Quels types d’allocations familiales sont versés ? -> FAK_EAK_AGENT
À combien s’élèvent les allocations familiales ? -> FAK_EAK_AGENT
Les allocations sont-elles déterminées en fonction du canton de domicile ou du canton de travail ? -> FAK_EAK_AGENT
Qui a droit aux allocations familiales ? -> FAK_EAK_AGENT
Quel parent perçoit les allocations familiales ? -> FAK_EAK_AGENT
Comment pouvez-vous faire valoir votre droit aux allocations familiales auprès de la Caisse d’allocations familiales de la Caisse fédérale de compensation (CAF-CFC) ? -> FAK_EAK_AGENT
Comment pouvez-vous prolonger un droit existant aux allocations de formation ? -> FAK_EAK_AGENT
Comment sont versées les allocations familiales de la caisse d’allocations familiales de la Caisse fédérale de compensation ? -> FAK_EAK_AGENT

# Question
{query}

# Intention
{intent}

# Thème
{tags}

# Historique de conversation
{conversational_memory}"""

AGENT_HANDOFF_PROMPT_IT = """# Compito"""


RAG_FOLLOWUP_AGENT_PROMPT_DE = """# Aufgabe"""


RAG_FOLLOWUP_AGENT_PROMPT_FR = """# Tâche
Votre tâche consiste à évaluer si la question suivante est formulée de manière suffisamment claire et précise pour effectuer une recherche sémantique dans une base de données vectorielle. Si la question est ambiguë ou nécessite des clarifications supplémentaires, vous devez poser des questions de suivi pour obtenir des informations supplémentaires.

1. Déterminez le thème de la question
2. Déterminez si la la question nécessite une question de suivi
3. Formulez une question de suivi courte et précise pour obtenir des informations supplémentaires

Vous pouvez également consulter l'historique de conversation pour obtenir des informations contextuelles supplémentaires.

# Format de réponse
theme: str - Thème de la question (e.g. "Splitting", "Bonifications pour tâches d'assistance", "Bonifications pour tâches éducatives", "Compte Individuel", etc.)
followup: bool (True/False) - Indique si la question nécessite des clarifications ou des informations supplémentaires.
question_de_suivi: str - Question de suivi courte et précise pour obtenir des informations supplémentaires.

# Exemples de thèmes et questions de suivi
Thème: Compte Individuel (CI)
Comment puis-je vérifier mes cotisations ? -> Souhaitez-vous obtenir un extrait de votre compte individuel (CI) pour vérifier vos cotisations ?
Est-ce que quelqu'un peut consulter mon compte individuel ? -> Souhaitez-vous savoir qui a accès à votre compte individuel (CI) ?
Où puis-je obtenir mon relevé de compte ? -> Souhaitez-vous savoir auprès de quelle caisse de compensation vous pouvez demander votre extrait de compte ?
Si je remarque une erreur sur mon compte, puis-je la corriger ? -> Souhaitez-vous savoir comment demander une rectification des inscriptions sur votre compte individuel (CI) ?
Mon employeur a-t-il bien déclaré mes salaires ? -> Voulez-vous vérifier si votre employeur a correctement annoncé vos revenus à la caisse de compensation ?
Que faire si je conteste les informations sur mon extrait ? -> Voulez-vous savoir comment contester ou faire rectifier les inscriptions sur votre compte individuel ?

Thème: Splitting:
Comment fonctionne le partage des revenus après un divorce ? -> Souhaitez-vous savoir quand le partage des revenus est effectué ou comment il est calculé ?
Que dois-je faire après mon divorce concernant mes cotisations ? -> Souhaitez-vous savoir comment demander le partage des revenus auprès de la caisse de compensation ?
Est-ce que je dois faire la demande avec mon ex-conjoint pour le partage des revenus ? -> Souhaitez-vous savoir si vous pouvez demander le partage des revenus individuellement ou si vous devez le faire conjointement ?
Que se passe-t-il si je ne fais pas de demande pour le partage des revenus ? -> Souhaitez-vous savoir si le partage des revenus sera effectué automatiquement si vous ne le demandez pas ?
Est-ce que mes revenus seront partagés si mon mariage a duré moins de deux ans ? -> Pouvez-vous me préciser les dates de votre mariage et de votre divorce pour déterminer si le partage s'applique ?
À quel moment le partage des revenus est-il effectué si mon ex-conjoint est décédé ? -> Souhaitez-vous savoir si le partage des revenus a lieu lorsque vous atteignez l'âge de référence ou si vous avez droit à une rente d'invalidité ?

Thème: Bonifications pour tâches d'assistance:
Comment puis-je obtenir une aide pour m'occuper d'un proche ? -> Votre proche reçoit-il une allocation pour impotence et habitez-vous à proximité l'un de l'autre ?
Puis-je avoir des bonifications si je m'occupe de mes parents âgés ? -> Est-ce que vos parents reçoivent une allocation pour impotence et vivez-vous à moins de 30 km d'eux ?
Quel est le montant de la bonification pour tâches d'assistance ? -> Souhaitez-vous connaître le montant précis ou comment il est calculé ?
Dois-je faire une demande chaque année pour les bonifications ? -> Voulez-vous savoir où et comment faire votre demande annuelle ?
Est-ce que je peux obtenir la bonification si je m'occupe de mon partenaire ? -> Vivez-vous en ménage commun avec votre partenaire depuis au moins cinq ans sans interruption ?
Quelles conditions faut-il remplir pour avoir droit aux bonifications ? -> Souhaitez-vous connaître les critères liés à la proximité de domicile et à l'état de la personne aidée ?

Thème: Bonifications pour tâches éducatives:
Comment puis-je obtenir une aide pour mes enfants ? -> Exercez-vous l'autorité parentale et êtes-vous marié(e), divorcé(e) ou non marié(e) avec l'autre parent ?
Qui reçoit la bonification si on est séparés ? -> Avez-vous une décision des autorités ou une convention sur l'attribution des bonifications pour tâches éducatives ?
Comment la bonification est-elle répartie entre les parents ? -> Exercez-vous l'autorité parentale conjointe avec l'autre parent, et avez-vous conclu une convention sur l'attribution des bonifications ?
Que faire si on ne se met pas d'accord sur les bonifications pour les enfants ? -> Souhaitez-vous savoir comment l'APEA intervient en l'absence d'accord entre les parents ?
Peut-on modifier l'attribution des bonifications pour nos enfants ? -> Souhaitez-vous conclure une nouvelle convention avec l'autre parent concernant l'attribution des bonifications ?
Comment les bonifications sont-elles calculées si j'ai plusieurs enfants ? -> Voulez-vous savoir si les bonifications pour tâches éducatives se cumulent pour chaque enfant ?
Dois-je informer la caisse de compensation si ma situation familiale change ? -> Souhaitez-vous savoir si vous devez signaler les changements concernant les bonifications pour tâches éducatives ?
Que se passe-t-il si je suis le seul à m'occuper des enfants ? -> Exercez-vous l'autorité parentale exclusive, et êtes-vous marié(e), divorcé(e) ou non marié(e) avec l'autre parent ?

Thème: Cotisations salariales à l’AVS, à l’AI et aux APG:
À partir de quel âge doit-on commencer à payer des cotisations ? -> Pouvez-vous me dire en quelle année vous êtes né(e) ?
Quand est-ce que je peux arrêter de cotiser à l'AVS ? -> Êtes-vous un homme ou une femme, et quelle est votre année de naissance ?
Je continue à travailler après ma retraite, dois-je encore payer des cotisations ? -> Avez-vous atteint l'âge de référence et exercez-vous toujours une activité lucrative ?
Comment fonctionne la franchise pour les retraités qui travaillent ? -> Souhaitez-vous connaître le montant de la franchise ou savoir comment elle s'applique ?
Est-ce que je dois payer des cotisations si je gagne très peu ? -> Quel est le montant annuel de votre salaire pour chaque emploi ?
Comment puis-je simplifier le paiement des cotisations ? -> Vos salariés gagnent-ils chacun moins de 22 050 francs par an, et le total des salaires ne dépasse-t-il pas 58 800 francs par an ?
À quelle fréquence dois-je payer les cotisations ? -> Quel est le montant total annuel des salaires que vous versez à vos employés ?
Que se passe-t-il si je paie mes cotisations en retard ? -> Souhaitez-vous connaître les intérêts moratoires applicables en cas de retard de paiement ?
Quels types de rémunérations sont soumis à cotisations ? -> Voulez-vous savoir si des primes ou des allocations spécifiques sont concernées ?
Les allocations familiales sont-elles soumises à cotisations ? -> Parlez-vous des allocations pour enfants ou de formation professionnelle conformes à l'usage local ou professionnel ?
Est-ce que les indemnités journalières sont soumises à cotisations ? -> Faites-vous référence aux indemnités journalières de l'AI, de l'AC ou aux allocations pour perte de gain ?
Les cadeaux de l'employeur sont-ils soumis à cotisations ? -> Pouvez-vous préciser le type de cadeaux et leur valeur approximative ?
Dois-je payer des cotisations sur une gratification reçue plus tard ? -> Cette gratification concerne-t-elle une période où vous étiez assuré et tenu de cotiser ?
Est-ce que les repas offerts par l'employeur sont soumis à cotisations ? -> Recevez-vous ces repas de manière régulière de la part de votre employeur ?
Je suis membre du conseil d'administration, comment mes cotisations sont-elles calculées ? -> Percevez-vous des honoraires ou des tantièmes pour cette fonction, et si oui, de quel montant ?
Est-ce que les allocations de déménagement sont soumises à cotisations ? -> Ces allocations sont-elles versées en raison d'un changement de domicile pour des raisons professionnelles ?
Comment sont évaluées les prestations en nature ? -> Recevez-vous des avantages comme la nourriture ou le logement de manière régulière ?
Les personnes qui travaillent dans une entreprise familiale paient-elles des cotisations ? -> Avez-vous moins de 20 ans et êtes-vous membre de la famille travaillant dans l'entreprise ?
Est-ce que les membres de la famille qui travaillent dans une exploitation agricole doivent cotiser ? -> Êtes-vous une personne seule, mariée, et avez-vous des enfants mineurs à charge ?
Dois-je payer des cotisations sur les allocations pour perte de gain versées en cas de service militaire ? -> Recevez-vous ces allocations directement ou par l'intermédiaire de votre employeur ?

Thème: Cotisations des indépendants à l’AVS, à l’AI et aux APG:
Est-ce que je suis considéré comme indépendant ? -> Pouvez-vous décrire votre activité professionnelle et si vous assumez les risques économiques ?
Dois-je payer des cotisations si je suis à mon compte ? -> Exercez-vous une activité lucrative en Suisse en tant qu'indépendant ?
À partir de quand dois-je commencer à cotiser ? -> Pouvez-vous me dire en quelle année vous êtes né(e) ?
Jusqu'à quel âge dois-je payer des cotisations ? -> Avez-vous atteint l'âge de référence et continuez-vous à exercer une activité lucrative ?
Quel est le taux de cotisation pour mon revenu ? -> Quel est votre revenu annuel provenant de votre activité indépendante ?
Je gagne très peu, combien dois-je cotiser ? -> Quel est votre revenu annuel provenant de votre activité indépendante ?
Je fais un petit travail indépendant en plus de mon emploi principal, dois-je cotiser dessus ? -> Quel est le montant annuel de votre revenu indépendant, et cotisez-vous déjà via votre emploi principal ?
Je suis à la retraite mais je travaille encore, dois-je cotiser ? -> Exercez-vous une activité lucrative après avoir atteint l'âge de référence, et souhaitez-vous savoir si vous devez cotiser ?
Comment fonctionne la franchise pour les retraités qui travaillent ? -> Souhaitez-vous connaître le montant de la franchise ou comment elle s'applique à vos revenus ?
Dois-je payer des cotisations sur les indemnités que je reçois ? -> Recevez-vous des allocations pour perte de gain ou des indemnités journalières de l'AI, de l'AC ou de l'assurance militaire ?

# Historique de conversation
{conversational_memory}

# Question
{query}"""

RAG_FOLLOWUP_AGENT_PROMPT_IT = """# """

FAK_EAK_FOLLOWUP_AGENT_PROMPT_DE = """# Aufgabe"""

FAK_EAK_FOLLOWUP_AGENT_PROMPT_FR = """# Tâche
Votre tâche consiste à poser des questions de suivi pour obtenir les informations nécessaires pour exécuter une fonction. Vous disposez des fonctions suivantes:
-


Si la question porte sur les allocations familiales, vérifiez que vous disposez des éléments suivants:
- Si la question porte sur les allocations familiales, vérifiez que vous disposez des éléments suivants:
    1. Questions sur le taux de réduction en cas d'anticipation de rente pour les femmes de la génération de transition:
        - date de naissance (datetime.date): La date de naissance de la femme (devrait être entre 1961 et 1969).
        - date de départ à la retraite (datetime.date): La date prévue pour le départ à la retraite.
        - revenu annuel moyen (float): Le revenu annuel moyen en CHF.
    2. Questions sur quel parent reçoit les allocations familiales:
        - 1 parent possède une activité lucrative OU les deux parents possèdent une activité lucrative ?
        - quel(s) parent(s) ont l'autorité parentale ?
        - les parents vivent-ils ensemble ?
        - un parent travaille dans le canton de domicile de l'enfant ?
        - 1 parent est salarité et l'autre indépendant OU les deux parents sont salariés OU les deux parents sont indépendants ?
        -

# Format de réponse

# Exemples


# Question
{query}"""

FAK_EAK_FOLLOWUP_AGENT_PROMPT_IT = """# """

PENSION_FUNCTION_CALLING_PROMPT_DE = """# Aufgabe
Ihre Aufgabe ist es, die richtige Funktion aufzurufen, um die vom Benutzer gestellte Frage zu beantworten. Sie müssen die Frage analysieren und die Parameter extrahieren/formatieren, die für den Aufruf der ausgewählten Funktion erforderlich sind.

# Verfügbare Funktionen
- determine_reduction_rate_and_supplement: Berechnet den Kürzungssatz und den Zuschlag für Frauen der Übergangsgeneration
- estimate_pension: Schätzt die Altersrente
- determine_reference_age: Bestimmt das Referenzalter (das Alter, in dem eine Person ihre Altersrente erhält)

# Signatur der Funktion
{func_metadata}

# Antwortformat
function_name(param1, param2, ...)

# Beispiele
Ich bin am 1962.31.12 geboren, möchte am 01.01.2025 in Rente gehen und mein Jahreseinkommen beträgt ca. 55'000 CHF. Wie hoch ist mein Kürzungssatz? -> calculate_reduction_rate_and_supplement("1962-12-31“, "2025-01-01", 55000.0)
Wie hoch ist mein Kürzungssatz, wenn ich am 1965-11-07 geboren bin, am 2026-04-15 in Rente gehen möchte und mein Jahreseinkommen 76200 beträgt? -> calculate_reduction_rate_and_supplement("1965-11-07", "2026-04-15", 76200.0)
Hier sind meine Informationen: Geburtsdatum 03.01.1968 und ich werde 2027 in Rente gehen. Ich verdiene etwa 90.000 CHF pro Jahr. Kann ich einen Zuschlag oder eine Ermäßigung erhalten? -> calculate_reduction_rate_and_supplement("1968-01-03", "2027-01-01", 90000.0)

# Frage
{query}"""

PENSION_FUNCTION_CALLING_PROMPT_FR = """# Tâche
Votre tâche consiste à appeler la fonction appropriée pour répondre à la question posée par l'utilisateur. Vous devez analyser la question et extraire/formatter les paramètres nécessaires pour appeler la fonction choisie.

# Fonctions disponibles
- determine_reduction_rate_and_supplement: Calcule le taux de réduction et le supplément pour les femmes de la génération de transition
- estimate_pension: Estime la rente de vieillesse
- determine_reference_age: Détermine l'âge de référence (âge auquel une personne perçoit sa rente de vieillesse)

# Signature de la fonction
{func_metadata}

# Format de réponse
function_name(param1, param2, ...)

# Exemples
Je suis née le 1962.31.12, je souhaite prendre ma retraite le 01.01.2025 et mon revenu annuel est d'environ 55'000 CHF. Quel est mon taux de réduction ? -> calculate_reduction_rate_and_supplement("1962-12-31", "2025-01-01", 55000.0)
Quel sera mon taux de réduction si je suis née le 1965-11-07, je souhaite prendre ma retraite le 2026-04-15 et mon revenu annuel est de 76200 ? -> calculate_reduction_rate_and_supplement("1965-11-07", "2026-04-15", 76200.0)
Voici mes informations: date de naissance le 03.01.1968 et je pars à la retraite en 2027. Je gagne environ 90000 CHF par an. Puis-je bénéficier d'un supplément ou taux de réduction ? -> calculate_reduction_rate_and_supplement("1968-01-03", "2027-01-01", 90000.0)

# Question
{query}"""

PENSION_FUNCTION_CALLING_PROMPT_IT = """# Compito
Il compito consiste nel chiamare la funzione appropriata per rispondere alla domanda posta dall'utente. Dovete analizzare la domanda ed estrarre/formattare i parametri necessari per chiamare la funzione scelta.

# Funzioni disponibili
- determine_reduction_rate_and_supplement: calcola il tasso di riduzione e il supplemento per le donne della generazione di transizione
- estimate_pension: stima la pensione di vecchiaia
- determine_reference_age: determina l'età di riferimento (l'età in cui una persona riceve la pensione di vecchiaia)

# Firma della funzione
{func_metadata}

# Formato della risposta
function_name(param1, param2, ...)

# Esempi
Sono nato il 31.12.1962, voglio andare in pensione il 01.01.2025 e il mio reddito annuo è di circa 55.000 franchi. Qual è il mio tasso di riduzione? -> calculate_reduction_rate_and_supplement("1962-12-31", "2025-01-01", 55000.0)
Qual è il mio tasso di riduzione se sono nato il 1965-11-07, voglio andare in pensione il 2026-04-15 e il mio reddito annuo è di 76200? -> calculate_reduction_rate_and_supplement("1965-11-07", "2026-04-15", 76200.0)
Ecco i miei dati: sono nato il 03.01.1968 e andrò in pensione nel 2027. Guadagno circa 90.000 franchi all'anno. Posso beneficiare di un supplemento o di un'aliquota di riduzione? -> calculate_reduction_rate_and_supplement("1968-01-03", "2027-01-01", 90000.0)

# Domanda
{query}"""

FAK_EAK_FUNCTION_CALLING_PROMPT_DE = """# Aufgabe"""

FAK_EAK_FUNCTION_CALLING_PROMPT_FR = """# Tâche
Votre tâche consiste à appeler la fonction appropriée pour répondre à la question posée par l'utilisateur. Vous devez analyser la question et extraire/formatter les paramètres nécessaires pour appeler la fonction choisie.

# Fonctions disponibles
- determine_child_benefits_eligibility: Détermine l'éligibilité aux allocations familiales pour les parents

# Signature de la fonction
{func_metadata}

# Format de réponse
function_name(param1, param2, ...)

# Exemples


# Question
{query}"""

FAK_EAK_FUNCTION_CALLING_PROMPT_IT = """# Compito"""

STATIC_WORKERS_SNOWBALL_PROMPT_FR = """# Tâche
Votre tâche consiste à poser des questions de suivi pour obtenir les informations nécessaires.
-> read predefined plan (human): see mermaid diagram
-> follow plan steps
    -> collect information
    -> execute actions
    -> collect output
    -> reflect on output
    -> refine/critique plan
    -> continue snowballing (repeat)"""

PLANNER_PROMPT_FR = """# Tâche"""

DYNAMIC_WORKERS_SNOWBALL_PROMPT_FR = """# Tâche
-> create plan (agent) -> PLANNER_PROMPT
-> follow plan steps
    -> collect information
    -> execute actions
    -> collect output
    -> reflect on output
    -> refine/critique plan
    -> continue snowballing (repeat)

A[Start]
B{Base Information/Plan -> Human or AI}
C[Snowball prompt 1]
D[Snowball prompt 2]
E[Snowball prompt 3]
F[Reflect on output]
G[Refine/Critique/Update plan] -> Optionally loop back to B
H[Summary/Format prompt]
I[End]

A --> B --> C --> D --> E --> F --> G --> B --> C --> ... --> H --> I

Execute tasks in parallel (eg. retrieval with GraphRAG, HippoRAG, etc.)"""

PLANNING_PROMPT_FR = """# Tâche
Votre tâche consiste à créer un plan pour répondre à la question posée par l'utilisateur. Vous devez déterminer les étapes nécessaires pour collecter les informations, exécuter les actions, collecter les résultats, réfléchir sur les résultats, affiner/critiquer le plan et continuer à faire avancer la boule de neige.

# Objecif et contexte
RAG

# Fonctions à disposition
fonctions

# Format d'appel de fonctions
<function_call>function_name(param1, param2, ...)</function_call>

# Format de réponse
1. <étape 1>
2. <étape 2>
...
N. <étape N>

# Exemple
Question: xxx
1. Identifier les mots-clés pertinents pour la recherche: "xxx"
2. Réformuler plusieurs version de la question pour une recherche sématique plus précise avec les mots-clés.
3. Effectuer une recherche sémantique dans la base de données vectorielle: <function_call>semantic_search(xxx)</function_call>
4. Evaluer la pertinence des résultats de la recherche.
5. Si les documents ne sont pas pertinents, demander à l'utilisateur des informations supplémentaires pour affiner la recherche et répéter les étapes 2 à 4.
6. Répondre à la question de l'utilisateur.

1. Collecter les informations sur la situation de l'utilisateur.
2. Poser des questions de suivi pour obtenir des détails supplémentaires.
3. Identifier les agents appropriés pour répondre à la question.
4. Transférer la conversation à l'agent approprié.
5. Suivre la conversation pour s'assurer que l'utilisateur obtient la réponse souhaitée.
6. Critiquer et réfléchir à la pertinence des documents obtenus pour pouvoir fournir une réponse de qualité.
6. Répondre à l'utilisateur avec les informations demandées.

1. Identifier les éléments clés de la question.
2. Déterminer si la question nécessite des clarifications ou des informations supplémentaires.
3. Formuler une question de suivi pour obtenir des informations supplémentaires.
4. Utiliser l'outil approprié pour répondre à la question.
5. Répondre à la question de l'utilisateur.

Ces exemples servent de marche à suivre générale mais peuvent être ajustés en fonction de la complexité de la question et des informations disponibles.

# Question
{query}

PLAN: """

PLAN_PARSER_PROMPT_FR = """# Tâche
Votre tâche consiste à"""

AGENT_EXECUTOR_PROMPT_FR = """# Tâche
Votre tâche consiste à exécuter les étapes du plan pour répondre à la question posée par l'utilisateur. Si une étape consiste à appeler une fonction (<function_call>...</function_call>)

# Plan
{plan}

"""

X = """
THINK/PLAN LIKE A HUMAN: WHAT WOULD A HUMAN NEED/DO TO ANSWER? methodology
1. High level planning: Define available tools/actions
2. Plan parser into steps, generate tags for step execution
3. inject results into EXECUTOR_PROMPT
4. Analyze/critique information and decide on action (<ask_followup_q>, <retrieval>, <answer>, etc.)
"""


MULTIPLE_SOURCE_VALIDATION_PROMPT_FR = """# Tâche
Votre tâche consiste à valider les sources d'information pour répondre à la question posée par l'utilisateur. Vous devez vérifier la fiabilité et la pertinence des sources pour garantir la qualité de la réponse.

# Format de réponse
Répondez avec une liste d'indices numérotés pour chaque source d'information valide. Par exemple: [1, 3, 5] ou [] si aucune source n'est valide. L'indexation commence à 0 (comme en Python).

# Note importante
Il se peut qu'aucune source ne puisse être validée. Dans ce cas, veuillez répondre avec une liste vide ([]).
Il se peut également que une ou plusieurs sources soient valides. Dans ce cas, veuillez répondre avec une liste d'indices correspondant à ces sources.

# Exemples
Question: Qu'est-ce qui change avec AVS 21?
Sources:
    0. Le 25 septembre 2022,le peuple et les cantons ont accepté la réforme AVS 21 et assuré ainsi un financement suffisant de l’AVS jusqu’à l’horizon 2030. La modification entrera en vigueur le 1er janvier 2024. La réforme comprenait deux objets : la modification de la loi sur l’assurance-vieillesse et survivants (LAVS) et l’arrêté fédéral sur le financement additionnel de l’AVS par le biais d’un relèvement de la TVA. Les deux objets étaient liés. Ainsi,le financement de l’AVS et le niveau des rentes seront garantis pour les prochaines années. L’âge de référence des femmes sera relevé à 65 ans,comme pour les hommes,le départ à la retraite sera flexibilisé et la TVA augmentera légèrement. La stabilisation de l’AVS comprend quatre mesures : \n\n• harmonisation de l’âge de la retraite (à l’avenir «âge de référence») des femmes et des hommes à 65 ans\n• mesures de compensation pour les femmes de la génération transitoire\n• retraite flexible dans l’AVS\n• financement additionnel par le relèvement de la TVA
    1. Vous pouvez déterminer votre droit aux prestations de façon simple et rapide,grâce au calculateur de prestations complémentaires en ligne : www.ahv-iv.ch/r/calculateurpc\n\n Le calcul est effectué de façon tout à fait anonyme. Vos données ne sont pas enregistrées. Le résultat qui en ressort constitue une estimation provisoire fondée sur une méthode de calcul simplifiée. Il s’agit d’une estimation sans engagement,qui ne tient pas lieu de demande de prestation et n’implique aucun droit. Le calcul n’est valable que pour les personnes qui vivent à domicile. Si vous résidez dans un home,veuillez vous adresser à sa direction,qui vous fournira les renseignements appropriés au sujet des prestations complémentaires.
Sources validées: [0]

Question: Quand des prestations complémentaires sont-elles versées ?
Sources:
    0. Lorsque la rente AVS ne suffit pas. Les rentes AVS sont en principe destinées à couvrir les besoins vitaux d'un assuré. Lorsque ces ressources ne sont pas suffisantes pour assurer la subsistance des bénéficiaires de rentes AVS,ceux-ci peuvent prétendre à des prestations complémentaires (PC).\n\nLe versement d'une telle prestation dépend du revenu et de la fortune de chaque assuré. Les PC ne sont pas des prestations d'assistance mais constituent un droit que la personne assurée peut faire valoir en toute légitimité lorsque les conditions légales sont réunies.
    1. La rente peut être anticipée ou ajournée. Anticipation de la rente : Femmes et hommes peuvent anticiper la perception de leur rente dès le premier jour du mois qui suit leur 63e anniversaire. Les femmes nées entre 1961 et 1969 pourront continuer à anticiper leur rente à 62 ans. Leur situation est régie par des dispositions transitoires spéciales. Pour plus d’informations à ce sujet,veuillez vous adresser à votre caisse de compensation. Durant la période d'anticipation,il n'existe pas de droit à une rente pour enfant. Ajournement de la rente : Les personnes qui ajournent leur retraite d'au moins un an et de cinq ans au maximum bénéficient d'une rente de vieilesse majorée d'une augmentation pendant toute la durée de leur retraite. Combinaison : Il est également possible de combiner l'anticipation et l'ajournement. Une partie de la rente de vieillesse peut être anticipée et une partie peut être ajournée une fois l'âge de référence atteint. Le montant de la réduction ou de la majoration de la rente est fixé selon le principe des calculs actuariels. Dans le cadre d'un couple,il est possible que l'un des conjoints anticipe son droit à la rente alors que l'autre l'ajourne.
    2. Quand des prestations complémentaires sont-elles versées ? Lorsque la rente AVS ne suffit pas. Les rentes AVS sont en principe destinées à couvrir les besoins vitaux d'un assuré. Lorsque ces ressources ne sont pas suffisantes pour assurer la subsistance des bénéficiaires de rentes AVS,ceux-ci peuvent prétendre à des prestations complémentaires (PC).\n\nLe versement d'une telle prestation dépend du revenu et de la fortune de chaque assuré. Les PC ne sont pas des prestations d'assistance mais constituent un droit que la personne assurée peut faire valoir en toute légitimité lorsque les conditions légales sont réunies.
    3. Si vous souhaitez vérifier que votre durée de cotisations ne présente pas de lacune ou que votre employeur a effectivement annoncé à la caisse de compensation les revenus sur lesquels vous avez cotisé, vous pouvez en tout temps demander par écrit un extrait de compte à une caisse de compensation ou sous www.avs-ai.ch. Il vous faut indiquer pour cela votre numéro AVS et votre adresse postale.
Sources validées: [2]

# Sources
{sources}

# Question
{query}"""


UNIQUE_SOURCE_VALIDATION_PROMPT_DE = """# Aufgabe
Ihre Aufgabe ist es, die Informationsquelle zur Beantwortung der vom Nutzer gestellten Frage zu validieren. Sie müssen feststellen:
- ob die Quelle relevant ist und die Informationen enthält, die zur Beantwortung der Frage notwendig sind.
- ob die Quelle teilweise (enthält nicht alle notwendigen Informationen) oder vollständig ist.
- den Grund für die Validierung der Quelle.

Seien Sie bei der Validierung äußerst streng. Validieren Sie eine Quelle nur, wenn Sie genaue Passagen aus der Quelle zitieren könnten, um die Frage zu beantworten.

Sie können auch die mit der Quelle verbundenen Themen konsultieren, um bei der Validierung der Quelle zu helfen, aber Ihre Entscheidung sollte sich hauptsächlich auf den Inhalt der Quelle selbst stützen.

# Format der Antwort
UniqueSourceValidation(
    is_partial: bool, # True, wenn die Quelle Teilinformationen enthält, False sonst.
    is_valid: bool # True, wenn die Quelle gültig ist, False sonst.
    reason: str # Begründung für die Validierung der Quelle (ein kurzer Satz)
)

# Themen
{tags}

# Quelle
{source}

# Frage
{query}"""


UNIQUE_SOURCE_VALIDATION_PROMPT_FR = """# Tâche
Votre tâche consiste à valider la source d'information pour répondre à la question posée par l'utilisateur. Vous devez déterminer :
- si la source est pertinente et contient l'information nécessaire pour répondre à la question.
- si la source est partielle (ne contient pas toutes les informations nécessaires) ou complète.
- la raison de la validation de la source.

Soyez extrêmement strict dans votre validation. Validez une source seulement si vous pourriez citer des passages exacts de la source pour répondre à la question.

Vous pouvez également consulter les sujets associés à la source pour aider à valider la source, mais votre décision doit principalement reposer sur le contenu de la source elle-même.

# Format de réponse
UniqueSourceValidation(
    is_partial: bool, # True si la source contient des informations partielles, False sinon
    is_valid: bool # True si la source est valide, False sinon
    reason: str # Raison de la validation de la source (une phrase courte)
)

# Sujets
{tags}

# Source
{source}

# Question
{query}"""


UNIQUE_SOURCE_VALIDATION_PROMPT_IT = """## Compito
Il vostro compito è quello di convalidare la fonte delle informazioni per rispondere alla domanda posta dall'utente. Dovete determinare se:
- se la fonte è pertinente e contiene le informazioni necessarie per rispondere alla domanda.
- se la fonte è parziale (non contiene tutte le informazioni necessarie) o completa.
- il motivo della convalida della fonte.

Siate estremamente rigorosi nella convalida. Convalidate una fonte solo se potete citarne i passaggi esatti per rispondere alla domanda.

Per convalidare la fonte si possono anche consultare gli argomenti ad essa associati, ma la decisione deve basarsi principalmente sul contenuto della fonte stessa.

# Formato della risposta
UniqueSourceValidation(
    is_partial: bool, # True se la fonte contiene informazioni parziali, False altrimenti
    is_valid: bool # True se la fonte è valida, False altrimenti
    reason: str # Motivo della convalida della fonte (una breve frase)
)

# Argomenti
{tags}

# Fonte
{source}

# Domanda
{query}"""
