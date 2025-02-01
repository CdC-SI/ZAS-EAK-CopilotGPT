SUMMARY_MEMORY_PROMPT_DE = """<instruktion>
    <instruktion>Ihre Aufgabe ist es, das folgende <konversation> zusammenzufassen und die wichtigsten Punkte zu erfassen.</instruktion>
    <instruktion>Die wichtigen Informationen, die Sie festhalten sollten, sind: das allgemeine Thema des Gesprächs, die gestellten Fragen und die gegebenen Antworten.</instruktion>
</instruktion>

<konversation>
{conversational_memory}
</konversation>"""


SUMMARY_MEMORY_PROMPT_FR = """<instructions>
    <instruction>Vôtre tâche consiste à résumer la <conversation> suivante en capturant les points essentiels.</instruction>
    <instruction>Les informations importantes à conserver sont: le thème général de la conversation, les questions posées, les réponses fournies.</instruction>
</instructions>

<conversation>
{conversational_memory}
</conversation>"""


SUMMARY_MEMORY_PROMPT_IT = """<istruzioni>
    <istruzione>Il tuo compito è quello di riassumere la seguente <conversazione> cogliendone i punti chiave.</istruzione>
    <istruzione> Le informazioni importanti da conservare sono: il tema generale della conversazione, le domande poste e le risposte date.<istruzione>
</istruzioni>

<conversazione>
{conversational_memory}
</conversazione>"""


TEST = """<instructions>
    <instruction>Vôtre tâche consiste à résumer la <conversation> suivante en capturant les points essentiels.</instruction>
    <instruction>Les informations importantes à conserver sont: le thème général de la conversation, les questions posées, les réponses fournies, les actions à entreprendre, les décisions prises, les informations manquantes, les informations erronées, les informations à vérifier, les informations à confirmer, les informations à compléter, les informations à corriger, les informations à supprimer, les informations à ajouter, les informations à reformuler, les informations à clarifier, les informations à synthétiser.</instruction>
</instructions>"""
