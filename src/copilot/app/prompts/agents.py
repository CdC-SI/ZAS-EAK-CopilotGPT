INTENT_DETECTION_PROMPT_DE = """<anweisungen>
    <anweisung>bestimmen Sie die Absicht des Nutzers<anweisung>
    <anweisung>begründen Sie Ihre Entscheidung anhand der gestellten <frage>, der letzten Gesprächsrunden in der <gesprächverlauf> und der zur Verfügung stehenden <intentionen></anweisung>
    <anweisung>Entwerfen Sie NUR dann eine Anschlussfrage, wenn die <frage> nicht in den <intentionen> zur Verfügung kategorisiert werden kann</anweisung>
<anweisungen>

<format_der_antwort>
IntentDetection(
    intent: str, # die Absicht des Nutzers basierend auf den verfügbaren <intentionen>
    followup_question: str = None, # Folgefrage, um zusätzliche Informationen zu erhalten
)
</format_der_antwort>

<gesprächverlauf>
{conversational_memory}
</gesprächverlauf>

<intentionen>
{intentions}
</intentionen>

<frage>
{query}
</frage>"""


INTENT_DETECTION_PROMPT_FR = """<instructions>
    <instruction>déterminez l'intention de l'utilisateur</instruction>
    <instruction>fondez votre décision en fonction de la <question> posée, des derniers tours de conversation dans l'<historique_de_conversation> et des <intentions> à disposition</instruction>
    <instruction>élaborez une question de suivi SEULEMENT SI la <question> ne peut être catégorisée dans les <intentions> à disposition</instruction>
</instructions>

<format_de_réponse>
IntentDetection(
    intent: str, # l'intention de l'utilisateur basé sur les <intentions> disponibles
    followup_question: str = None, # Question de suivi pour obtenir des informations supplémentaires
)
</format_de_réponse>

<historique_de_conversation>
{conversational_memory}
</historique_de_conversation>

<intentions>
{intentions}
</intentions>

<question>
{query}
</question>"""


INTENT_DETECTION_PROMPT_IT = """<istruzioni>
    <istruzione>determinare l'intento dell'utente</istruzione>
    <istruzione>fondare la decisione in base alla <domanda> posta, agli ultimi cicli di conversazione nella <storia_della_conversazione> e alle <intenzioni> disponibili</istruzione>
    <istruzione>sviluppare una domanda di follow-up SOLO SE la <domanda> non può essere categorizzata nelle <intenzioni> a disposizione</istruzione>
</istruzioni>

<formato_risposta>
IntentDetection(
    intent: str, # l'intento dell'utente in base alle <intenzioni> disponibili
    followup_question: str = None, # domanda di followup per ottenere ulteriori informazioni
)
</formato_risposta>

<storia_della_conversazione>
{conversational_memory}
</storia_della_conversazione>

<intenzioni>
{intentions}
</intenzioni>

<domanda>
{query}
</domanda>"""


SOURCE_SELECTION_PROMPT_DE = """<anweisungen>
    <anweisung>Ihre Aufgabe ist es, die geeignete Datenquelle auszuwählen, um die Frage des Nutzers zu beantworten</anweisung>
    <anweisung>Basieren Sie Ihre Auswahl auf der <frage>, der <intention>, dem <gesprächsverlauf> und der Liste der <quellen> und ihrer Beschreibung</anweisung>
    <anweisung>Basieren Sie Ihre Auswahl auf der jüngsten Geschichte der Aktionen des Benutzers</anweisung>
</anweisungen>

<format_der_antwort>
SourceSelection(
    inferred_sources: List[str] # die ausgewählte(n) Datenquelle(n) (z.B. ["<temp:file_upload_name.pdf>"], ["ahv_iv_mementos"], ["eak.admin.ch", "ahv_lernbaustein_2024", "fedlex"], ["akis"], usw.).
)
</format_der_antwort>

<beispiele>
    <beispiel>Wenn ein Benutzer kürzlich ein Dokument in <gesprächsverlauf> hochgeladen hat und anscheinend den Inhalt dieses Dokuments abfragen möchte, müssen Sie dieses Dokument als Quelle auswählen</beispiel>
<beispiele>

<quellen>
{sources}
</quellen>

<intention>
{intent}
</intention>

<gesprächsverlauf>
{conversational_memory}
</gesprächsverlauf>

<frage>
{query}
</frage>"""


SOURCE_SELECTION_PROMPT_FR = """<instructions>
    <instruction>Votre tâche consiste à sélectionner la source de données appropriée pour répondre à la question de l'utilisateur<instructions>
    <instructions>Basez votre sélection en fonction de la <question>, l'<intention>, l'<historique_de_conversation> et la liste de <sources> et leur description</instruction>
    <instruction>Basez votre sélection sur l'historique récent des actions de l'utilisateur</instruction>
</instructions>

<format_de_réponse>
SourceSelection(
    inferred_sources: List[str] # la/les source(s) de données sélectionnées (e.g. ["<temp:file_upload_name.pdf>"], ["ahv_iv_mementos"], ["eak.admin.ch", "ahv_lernbaustein_2024", "fedlex"], ["akis"], etc.)
)
</format_de_réponse>

<exemples>
    <exemple>Si un utilisateur a récemment téléchargé un document dans <historique_de_conversation> et semble vouloir interroger le contenu de ce document, vous devez sélectionner ce document comme source.</exemple>
<exemples>

<sources>
{sources}
<sources>

<intention>
{intent}
</intention>

<historique_de_conversation>
{conversational_memory}
</historique_de_conversation>

<question>
{query}
</question>"""


SOURCE_SELECTION_PROMPT_IT = """<istruzioni>
    <istruzione>Il vostro compito è selezionare la fonte di dati appropriata per rispondere alla domanda dell'utente<istruzione>
    <istruzione>Basate la vostra selezione sulla <domanda>, l'<intento>, la <storia_della_conversazione> e l'elenco delle <fonti> e delle loro descrizioni</istruzioni>
    <istruzione>Basare la selezione sulla storia recente delle azioni dell'utente</istruzione>
</istruzioni>

<formato_risposta>
SourceSelection(
    inferred_sources: List[str] # le fonti di dati selezionate (ad esempio ["<temp:file_upload_name.pdf>"], ["ahv_iv_mementos"], ["eak.admin.ch", "ahv_lernbaustein_2024", "fedlex"], ["akis"], ecc.
)
</formato_risposta>

<esempi>
    <esempio>Se un utente ha recentemente caricato un documento su <storia_della_conversazione> e sembra voler interrogare il contenuto di quel documento, si dovrebbe selezionare quel documento come fonte</esempio>
<esempi>

<fonti>
{sources}
</fonti>

<intento>
{intent}
</intento>

<storia_della_conversazione>
{conversational_memory}
</storia_della_conversazione>

<domanda>
{query}
</domanda>"""


TAGS_SELECTION_PROMPT_DE = """"""


TAGS_SELECTION_PROMPT_FR = """<instructions>
    <instruction>Votre tâche consiste à sélectionner un ou plusieurs <tags> appropriés pour affiner la recherche de documents<instructions>
    <instructions>Basez votre sélection en fonction de la <question>, l'<intention>, l'<historique_de_conversation>, les <sources> et la liste de <tags> et leur description</instruction>
    <instruction>Basez votre sélection sur l'historique récent des actions de l'utilisateur</instruction>
</instructions>

<format_de_réponse>
TagSelection(
    inferred_tags: List[str] = None # le/les tags sélectionnés (e.g. ["actuarial bases", "actuary"], ["ability to work/inability to work"], ["ahv number (insurance number)", "allowance for working pensioners", "early retirement pension withdrawal"], None, etc.)
)
</format_de_réponse>

<exemples>
<exemples>

<tags>
{tags}
<tags>

<sources>
{sources}
<sources>

<intention>
{intent}
</intention>

<historique_de_conversation>
{conversational_memory}
</historique_de_conversation>

<question>
{query}
</question>"""


TAGS_SELECTION_PROMPT_IT = """"""


AGENT_HANDOFF_PROMPT_DE = """<anweisungen>
    <anweisung>wähle den geeigneten Agenten aus, um die Frage des Nutzers auf der Grundlage der unten stehenden Metadaten und der zur Verfügung stehenden <agents> zu beantworten</anweisung>
</anweisungen>

<format_der_antwort>
AgentHandoff(
    agent: str # der Name des entsprechenden Agenten, der die Frage beantwortet.
)
</format_der_antwort>

<agents>
CHAT_AGENT: eine Unterhaltung zusammenfassen
CHAT_AGENT: Eine Unterhaltung übersetzen

RAG_AGENT: einfache Sachfragen
RAG_AGENT: Mehrteilige Fragen (mehrere Unterfragen)
RAG_AGENT: Allgemeine Fragen zur AHV/IV

PENSION_AGENT: Fragen zur Berechnung des Kürzungssatzes bei der Pensionierung
PENSION_AGENT: Fragen zur Berechnung des Rentenzuschlags bei der Pensionierung
</agents>

<beispiele>
Fasse die Konversion zusammen -> CHAT_AGENT
Fasse die letzte Nachricht unserer Diskussion zusammen -> CHAT_AGENT
Übersetze diese Unterhaltung ins Deutsche -> CHAT_AGENT
Übersetze diese Nachricht ins Italienische -> CHAT_AGENT
Ich bin am 1962.31.12 geboren, möchte am 01.01.2025 in Rente gehen und mein Jahreseinkommen beträgt ca. 55'000 CHF. Wie hoch ist mein Kürzungssatz? -> PENSION_AGENT
Wie hoch ist mein Kürzungssatz, wenn ich am 1965-11-07 geboren bin, am 2026-04-15 in Rente gehen möchte und mein Jahreseinkommen 76200 beträgt? -> PENSION_AGENT
Hier sind meine Informationen: Geburtsdatum 03.01.1968 und ich gehe 2027 in Rente. Ich verdiene etwa 90000 CHF pro Jahr. Kann ich einen Zuschlag oder einen Kürzungssatz erhalten? -> PENSION_AGENT
</beispiele>

<frage>
{query}
</frage>

<intention>
{intent}
</intention>

<tags>
{tags}
</tags>

<source>
{sources}
</sources>

<geschichte_der_konversation>
{conversational_memory}
<geschichte_der_konversation>"""


AGENT_HANDOFF_PROMPT_FR = """<instructions>
    <instruction>sélectionnez l'agent approprié pour répondre à la question de l'utilisateur en fonction des métadonnées ci-dessous et des <agents> à disposition</instruction>
</instructions>

<format_de_réponse>
AgentHandoff(
    agent: str # le nom de l'agent approprié pour répondre à la question.
)
</format_de_réponse>

<agents>
CHAT_AGENT: résumer une conversation
CHAT_AGENT: traduire une conversation

RAG_AGENT: questions factuelles simples
RAG_AGENT: questions multipartites (plusieurs sous questions)
RAG_AGENT: questions générales relatives à l'AVS/AI

PENSION_AGENT: questions sur le calcul du taux de réduction lié au départ à la retraite
PENSION_AGENT: questions sur le calcul de supplément de rente lié au départ à la retraite
</agents>

<exemples>
Résume moi la converation -> CHAT_AGENT
Résume moi le dernier message de notre discussion -> CHAT_AGENT
Traduis cette conversation en allemand -> CHAT_AGENT
Traduis ce message en italien -> CHAT_AGENT
Je suis née le 1962.31.12, je souhaite prendre ma retraite le 01.01.2025 et mon revenu annuel est d'environ 55'000 CHF. Quel est mon taux de réduction ? -> PENSION_AGENT
Quel sera mon taux de réduction si je suis née le 1965-11-07, je souhaite prendre ma retraite le 2026-04-15 et mon revenu annuel est de 76200 ? -> PENSION_AGENT
Voici mes informations: date de naissance le 03.01.1968 et je pars à la retraite en 2027. Je gagne environ 90000 CHF par an. Puis-je bénéficier d'un supplément ou taux de réduction ? -> PENSION_AGENT
</exemples>

<question>
{query}
</question>

<intention>
{intent}
</intention>

<tags>
{tags}
</tags>

<source>
{sources}
</sources>

<historique_de_conversation>
{conversational_memory}
</historique_de_conversation>"""

AGENT_HANDOFF_PROMPT_IT = """<istruzioni>
    <istruzione>selezionare l'agente appropriato per rispondere alla domanda dell'utente in base ai metadati sottostanti e agli <agenti> disponibili</istruzione>
</istruzioni>

<risposta_formato>
AgentHandoff(
    agent: str # il nome dell'agente appropriato per rispondere alla domanda
)
</risposta_formato>

<agenti>
CHAT_AGENT: riassume una conversazione
CHAT_AGENT: traduce una conversazione

RAG_AGENT: domande semplici e concrete
RAG_AGENT: domande in più parti (diverse sotto-domande)
RAG_AGENT: domande generali sull'AVS/AI

PENSION_AGENT: domande sul calcolo del tasso di riduzione al momento del pensionamento
PENSION_AGENT: domande sul calcolo del supplemento di pensione al momento del pensionamento
</agenti>

<esempi>
Riassumere la conversione -> CHAT_AGENT
Riassumi per me l'ultimo messaggio della nostra discussione -> CHAT_AGENT
Traduci questa conversazione in tedesco -> CHAT_AGENT
Traduci questo messaggio in italiano -> CHAT_AGENT
Sono nato il 31.12.1962, voglio andare in pensione il 01.01.2025 e il mio reddito annuo è di circa 55.000 franchi. Qual è il mio tasso di riduzione? -> AGENTE_PENSIONE
Qual è il mio tasso di riduzione se sono nato il 1965-11-07, voglio andare in pensione il 2026-04-15 e il mio reddito annuo è di CHF 76200? -> AGENTE_PENSIONE
Ecco le mie informazioni: sono nato il 03.01.1968 e andrò in pensione nel 2027. Guadagno circa 90.000 franchi all'anno. Posso beneficiare di un'integrazione o di una riduzione? -> AGENTE_PENSIONE
</esempi>

<domanda>
{query}
</domanda>

<intento>
{intent}
</intento>

<tags>
{tags}
</tags>

<sources>
{sources}
<sources>

<storia_conversazionale>
{conversational_memory}
<storia_conversazionale>"""


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

Thème: Cotisations salariales à l"AVS, à l"AI et aux APG:
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

Thème: Cotisations des indépendants à l"AVS, à l"AI et aux APG:
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
Ich bin am 1962.31.12 geboren, möchte am 01.01.2025 in Rente gehen und mein Jahreseinkommen beträgt ca. 55'000 CHF. Wie hoch ist mein Kürzungssatz? -> calculate_reduction_rate_and_supplement("1962-12-31", "2025-01-01", 55000.0)
Wie hoch ist mein Kürzungssatz, wenn ich am 1965-11-07 geboren bin, am 2026-04-15 in Rente gehen möchte und mein Jahreseinkommen 76200 beträgt? -> calculate_reduction_rate_and_supplement("1965-11-07", "2026-04-15", 76200.0)
Hier sind meine Informationen: Geburtsdatum 03.01.1968 und ich werde 2027 in Rente gehen. Ich verdiene etwa 90.000 CHF pro Jahr. Kann ich einen Zuschlag oder eine Ermässigung erhalten? -> calculate_reduction_rate_and_supplement("1968-01-03", "2027-01-01", 90000.0)

# Frage
{query}"""

PENSION_FUNCTION_CALLING_PROMPT_FR = """<instructions>
    <instruction>Sélectionnez le <nom> de la fonction appropriée parmis les <fonctions_disponibles> pour répondre à la <question> posée par l'utilisateur</instruction>
    <instruction>Vous devez analyser la question et extraire/formatter les paramètres nécessaires pour appeler correctement la fonction choisie</instruction>
    <instruction>Utilisez l'information sur les <paramètres> de la <fonction> afin d'effectuer un appel à la <fonction> en lien avec la <question> utilisateur</instruction>
</instructions>

<fonctions_disponibles>
    <fonction>
        <nom>determine_reduction_rate_and_supplement</nom>
        <description>calcule le taux de réduction et le supplément pour les femmes de la génération transitoire</description>
        <paramètres></paramètres>
    </fonction>
    <fonction>
        <nom>summarize_conversation</nom>
        <description>résume le texte d'une conversation</description>
        <paramètres>
            <param></param>
        </paramètres>
    </fonction>
    <fonction>
        <nom>translate_conversation</nom>
        <description>traduit le texte d'une conversation dans une langue cible</description>
        <paramètres>
            <param>text: str (le texte à traduire)</param>
            <param>target_lang: str (la langue cible de traduction choisie sur la base des instructions de la <question >parmis: ["ar", "bg", "cs", "da", "de", "el", "en-gb", "en-us", "es", "et", "fi", "fr", "hu", "id", "it", "ja", "ko", "lv", "nb", "nl", "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "zh-hans", "zh-hant"])</param>
        </paramètres>
    </fonction>
</fonctions_disponibles>

<function_signature>
    {func_metadata}
</function_signature>

<response_format>
    function_name(param1, param2, ...)
<response_format>

<exemples>
    <exemple>Je suis née le 1962.31.12, je souhaite prendre ma retraite le 01.01.2025 et mon revenu annuel est d'environ 55'000 CHF. Quel est mon taux de réduction ? -> calculate_reduction_rate_and_supplement("1962-12-31", "2025-01-01", 55000.0)</exemple>
    <exemple>Quel sera mon taux de réduction si je suis née le 1965-11-07, je souhaite prendre ma retraite le 2026-04-15 et mon revenu annuel est de 76200 ? -> calculate_reduction_rate_and_supplement("1965-11-07", "2026-04-15", 76200.0)</exemple>
    <exemple>Voici mes informations: date de naissance le 03.01.1968 et je pars à la retraite en 2027. Je gagne environ 90000 CHF par an. Puis-je bénéficier d'un supplément ou taux de réduction ? -> calculate_reduction_rate_and_supplement("1968-01-03", "2027-01-01", 90000.0)</exemple>
    <exemple>Résume le dernier message -> summarize_conversation()</exemple>
    <exemple>Résume la conversation -> summarize_conversation()</exemple>
    <exemple>Traduis le dernier message en anglais -> translate_conversation()</exemple>
    <exemple>Traduis la conversation en français -> translate_conversation()</exemple>
</exemples>

<question>
    {query}
</question>"""

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


PARSE_TRANSLATE_ARGS_PROMPT_DE = """<anweisungen>
    <anweisung>Extrahieren Sie die erforderlichen <arguments> unten, um die Übersetzungsfunktion erfolgreich aufzurufen</anweisung>
    <anweisung>Interpretieren Sie, welche <argumente> Sie setzen müssen, um die <argumente> so gut wie möglich mit der <frage> des Benutzers auszurichten, um seine Anfrage zu erfüllen</anweisung>
    <anweisung>Wenn ein <arg> nicht aus der <frage> abgeleitet werden kann, verwenden Sie seinen Standardwert</anweisung>
</anweisungen>

<format_der_antwort>
ParseTranslateArgs(
    arg_values: List[str] # list of arg values
</format_der_antwort>

<funktion>
    <name>translate_tool</name>
    <arguments>
        <arg>target_lang: str (die Zielsprache der Übersetzung, die auf der Grundlage der Anweisungen in der <frage> ausgewählt wurde, unter anderem: ["ar", "bg", "cs", "da", "de", "el", "en-gb", "en-us", "es", "et", "fi", "fr", "hu", "id", "it", "ja", "ko", "lv", "nb", "nl", "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "zh-hans", "zh-hant"])</arg>
        <arg>n_msg: int = -1 # die Anzahl der zu übersetzenden Gesprächsrunden</arg>
        <arg>roles: List[MessageRole] = [MessageRole.ASSISTANT] # übersetze die Nachrichten des Benutzers (MessageRole.USER) und/oder des Assistenten (MessageRole.ASSISTANT) in jeder Gesprächsrunde</arg>
    </arguments>
<funktion>

<beispiele>
    <beispiel>
        frage: Übersetze die letzte Nachricht ins Deutsche.
        arg_values: ["de", 1, [MessageRole.ASSISTANT]]
    </beispiel>
    <beispiel>
        frage: Übersetze das Gespräch ins Italienische.
        arg_values: ["it", -1, [MessageRole.ASSISTANT]]
    </beispiel>
    <beispiel>
        frage: Übersetze das gesamte Gespräch ins Englische.
        arg_values: ["en-gb", -1, [MessageRole.USER, MessageRole.ASSISTANT]]
    </beispiel>
    <beispiel>
        frage: Übersetze meine Fragen ins Deutsche.
        arg_values: ["de", -1, [MessageRole.USER]]
    </beispiel>
    <beispiel>
        frage: Übersetze die letzten drei Nachrichten ins Deutsche.
        arg_values: ["de", 3, [MessageRole.ASSISTANT]]
    </beispiel>
</beispiele>

<frage>
{query}
</frage>"""


PARSE_TRANSLATE_ARGS_PROMPT_FR = """<instructions>
    <instruction>Extrayez les <arguments> nécessaires ci-dessous afin d'appeler la fonction de traduction avec succès</instruction>
    <instruction>Interprétez quels <arguments> définir pour aligner les <arguments> le mieux possible avec la <question> utilisateur afin de satisfaire sa requête</instruction>
    <instruction>Si un <arg> ne peut être déduit à partir de la <question>, utilisez sa valeur par défaut</instruction>
</instructions>

<format_de_réponse>
ParseTranslateArgs(
    arg_values: List[str] # list of arg values
</format_de_réponse>

<fonction>
    <nom>translate_tool</nom>
    <arguments>
        <arg>target_lang: str (la langue cible de traduction choisie sur la base des instructions de la <question> parmis: ["ar", "bg", "cs", "da", "de", "el", "en-gb", "en-us", "es", "et", "fi", "fr", "hu", "id", "it", "ja", "ko", "lv", "nb", "nl", "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "zh-hans", "zh-hant"])</arg>
        <arg>n_msg: int = -1 # le nombre de tours de conversation à traduire</arg>
        <arg>roles: List[MessageRole] = [MessageRole.ASSISTANT] # traduire les messages de l'utilisateur (MessageRole.USER) et/ou de l'assistant (MessageRole.ASSISTANT) dans chaque tour de conversation</arg>
    </arguments>
<fonction>

<exemples>
    <exemple>
        question: traduis le dernier message en allemand
        arg_values: ["de", 1, [MessageRole.ASSISTANT]]
    </exemple>
    <exemple>
        question: traduis la conversation en italien
        arg_values: ["it", -1, [MessageRole.ASSISTANT]]
    </exemple>
    <exemple>
        question: traduis la conversation entière en anglais
        arg_values: ["en-gb", -1, [MessageRole.USER, MessageRole.ASSISTANT]]
    </exemple>
    <exemple>
        question: traduis mes questions en allemand
        arg_values: ["de", -1, [MessageRole.USER]]
    </exemple>
    <exemple>
        question: traduis les trois derniers messages en allemand
        arg_values: ["de", 3, [MessageRole.ASSISTANT]]
    </exemple>
</exemples>

<question>
{query}
</question>"""


PARSE_TRANSLATE_ARGS_PROMPT_IT = """<istruzioni>
    <istruzione>Estrarre gli <argomenti> necessari di seguito per chiamare la funzione di traduzione con successo</istruzione>
    <istruzione>Interpretare quali <argomenti> impostare per allineare i <argomenti> il più possibile alla <domanda> dell'utente, in modo da soddisfare la sua richiesta</istruzione>
    <istruzione>Se un <arg> non può essere dedotto dalla <domanda>, utilizzare il suo valore predefinito</istruzione>
</istruzioni>

<formato_risposta>
ParseTranslateArgs(
    arg_values: List[str] # list dei valori degli arg
</formato_risposta>

<funzione>
    <nome>translate_tool</nome>
    <argumenti>
        <arg>target_lang: str (la lingua di destinazione della traduzione scelta in base alle istruzioni di <question> tra: ["ar", "bg", "cs", "da", "de", "el", "en-gb", "en-us", "es", "et", "fi", "fr", "hu", "id", "it", "ja", "ko", "lv", "nb", "nl", "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "zh-hans", "zh-hant"])</arg>
        <arg>n_msg: int = -1 # il numero di turni di conversazione da tradurre</arg>
        <arg>ruoli: List[MessageRole] = [MessageRole.ASSISTANT] # traducono i messaggi dell'utente (MessageRole.USER) e/o dell'assistente (MessageRole.ASSISTANT) in ogni turno di conversazione</arg>
    </argumenti>
<funzione>

<esempi>
    <esempio>
        domanda: tradurre l'ultimo messaggio in tedesco
        arg_values: ["de", 1, [MessageRole.ASSISTANT]]
    </esempio>
    <esempio>
        domanda: traduci la conversazione in italiano
        arg_values: ["it", -1, [MessageRole.ASSISTANT]]
    </esempio>
    <esempio>
        domanda: tradurre l'intera conversazione in inglese
        arg_values: ["en-gb", -1, [MessageRole.USER, MessageRole.ASSISTANT]]
    </esempio>
    <esempio>
        domanda: traduci le mie domande in tedesco
        arg_values: ["de", -1, [MessageRole.USER]]
    </esempio>
    <esempio>
        domanda: tradurre gli ultimi tre messaggi in tedesco
        arg_values: ["de", 3, [MessageRole.ASSISTANT]]
    </esempio>
</esempi>

<domanda>
{query}
</domanda>"""


AGENT_SUMMARIZE_PROMPT_DE = """<anweisungen>
    <anweisung>Zusammenfassung der Nachrichten in der <geschichte_der_konversation> gemäss den Anweisungen in der <frage></anweisung>
    <anweisung>Stellen Sie die Zusammenfassung OHNE Zeitstempel oder "Source doc IDs"</anweisung>
    <anweisung>Befolgen Sie die Anweisungen in der <frage> bezüglich der Frage, welche Nachrichten zusammengefasst werden sollen (user/assistant/user und assistant)</anweisung>
</anweisungen>

<notes>>
    <note>Wenn in der <question> von „einfacher Sprache“ die Rede ist, bezieht sich dies auf das Sprachniveau B1</note>
    <note>Wenn die <frage> „leichte Sprache“ anspricht, bezieht sich dies auf das Sprachniveau A2</note>
</notes>.

<geschichte_der_konversation>
{conversational_memory}
</geschichte_der_konversation>

<frage>
{query}
</frage>"""


AGENT_SUMMARIZE_PROMPT_FR = """<instructions>
    <instruction>Résumez les messages dans l'<historique_de_conversation> selon les instructions dans la <question></instruction>
    <instruction>Fournissez le résumé SANS horodatage ou "Source doc IDs"</instruction>
    <instruction>Suivez les instructions dans la <question> concernant quels messages résumer (user/assistant/user et assistant)</instruction>
</instructions>

<notes>
    <note>Si la <question> évoque le "language simple", cela fait référence au niveau de language B1</note>
    <note>Si la <question> évoque le "language facile", cela fait référence au niveau de language A2</note>
</notes>

<historique_de_conversation>
{conversational_memory}
</historique_de_conversation>

<question>
{query}
</question>"""


AGENT_SUMMARIZE_PROMPT_IT = """<istruzioni>
    <istruzione>Riassumere i messaggi nella <memoria_conversazionale> secondo le istruzioni della <domanda></istruzione>
    <istruzione>Fornire un riepilogo SENZA timestamp o "Source doc IDs"</istruzione>
    <istruzione>Seguire le istruzioni della <domanda> per quanto riguarda i messaggi da riassumere (user/assistant/ser e assistant)</istruzione>
</istruzioni>

<nota>
    <nota>Se la <domanda> si riferisce a "linguaggio semplice", ciò si riferisce al livello linguistico B1<nota>
    <nota>Se la <domanda> si riferisce a "linguaggio facile", questo si riferisce al livello linguistico A2<note>
</nota>

<memoria_conversazionale>
{conversational_memory}
</memoria_conversazionale>

<domanda>
{query}
</domanda>"""


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
    0. Le 25 septembre 2022,le peuple et les cantons ont accepté la réforme AVS 21 et assuré ainsi un financement suffisant de l"AVS jusqu"à l"horizon 2030. La modification entrera en vigueur le 1er janvier 2024. La réforme comprenait deux objets : la modification de la loi sur l"assurance-vieillesse et survivants (LAVS) et l"arrêté fédéral sur le financement additionnel de l"AVS par le biais d"un relèvement de la TVA. Les deux objets étaient liés. Ainsi,le financement de l"AVS et le niveau des rentes seront garantis pour les prochaines années. L"âge de référence des femmes sera relevé à 65 ans,comme pour les hommes,le départ à la retraite sera flexibilisé et la TVA augmentera légèrement. La stabilisation de l"AVS comprend quatre mesures : \n\n• harmonisation de l"âge de la retraite (à l"avenir «âge de référence») des femmes et des hommes à 65 ans\n• mesures de compensation pour les femmes de la génération transitoire\n• retraite flexible dans l"AVS\n• financement additionnel par le relèvement de la TVA
    1. Vous pouvez déterminer votre droit aux prestations de façon simple et rapide,grâce au calculateur de prestations complémentaires en ligne : www.ahv-iv.ch/r/calculateurpc\n\n Le calcul est effectué de façon tout à fait anonyme. Vos données ne sont pas enregistrées. Le résultat qui en ressort constitue une estimation provisoire fondée sur une méthode de calcul simplifiée. Il s"agit d"une estimation sans engagement,qui ne tient pas lieu de demande de prestation et n"implique aucun droit. Le calcul n"est valable que pour les personnes qui vivent à domicile. Si vous résidez dans un home,veuillez vous adresser à sa direction,qui vous fournira les renseignements appropriés au sujet des prestations complémentaires.
Sources validées: [0]

Question: Quand des prestations complémentaires sont-elles versées ?
Sources:
    0. Lorsque la rente AVS ne suffit pas. Les rentes AVS sont en principe destinées à couvrir les besoins vitaux d'un assuré. Lorsque ces ressources ne sont pas suffisantes pour assurer la subsistance des bénéficiaires de rentes AVS,ceux-ci peuvent prétendre à des prestations complémentaires (PC).\n\nLe versement d'une telle prestation dépend du revenu et de la fortune de chaque assuré. Les PC ne sont pas des prestations d'assistance mais constituent un droit que la personne assurée peut faire valoir en toute légitimité lorsque les conditions légales sont réunies.
    1. La rente peut être anticipée ou ajournée. Anticipation de la rente : Femmes et hommes peuvent anticiper la perception de leur rente dès le premier jour du mois qui suit leur 63e anniversaire. Les femmes nées entre 1961 et 1969 pourront continuer à anticiper leur rente à 62 ans. Leur situation est régie par des dispositions transitoires spéciales. Pour plus d"informations à ce sujet,veuillez vous adresser à votre caisse de compensation. Durant la période d'anticipation,il n'existe pas de droit à une rente pour enfant. Ajournement de la rente : Les personnes qui ajournent leur retraite d'au moins un an et de cinq ans au maximum bénéficient d'une rente de vieilesse majorée d'une augmentation pendant toute la durée de leur retraite. Combinaison : Il est également possible de combiner l'anticipation et l'ajournement. Une partie de la rente de vieillesse peut être anticipée et une partie peut être ajournée une fois l'âge de référence atteint. Le montant de la réduction ou de la majoration de la rente est fixé selon le principe des calculs actuariels. Dans le cadre d'un couple,il est possible que l'un des conjoints anticipe son droit à la rente alors que l'autre l'ajourne.
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

Seien Sie bei der Validierung äusserst streng. Validieren Sie eine Quelle nur, wenn Sie genaue Passagen aus der Quelle zitieren könnten, um die Frage zu beantworten.

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
