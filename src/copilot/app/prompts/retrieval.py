QUERY_REWRITING_PROMPT_DE = """Ihre Aufgabe ist es, {n_alt_queries} verschiedene Versionen der gegebenen Benutzeranfrage zu generieren, um relevante Dokumente aus einer Vektordatenbank zu finden. Indem Sie mehrere Perspektiven auf die Benutzerfrage erzeugen, wollen Sie dem Benutzer helfen, einige der Einschränkungen der entfernungsbasierten Ähnlichkeitssuche zu überwinden. Geben Sie diese alternativen Fragen IN DER GLEICHEN SPRACHE wie die URSPRÜNGLICHE FRAGE an, getrennt durch Zeilenumbrüche "\n". URSPRÜNGLICHE FRAGE: {query}"""


QUERY_REWRITING_PROMPT_FR = """Votre tâche consiste à générer {n_alt_queries} différentes versions de la requête utilisateur donnée pour extraire les documents pertinents d'une base de données vectorielle. En générant plusieurs perspectives sur la question de l'utilisateur, votre objectif est d'aider l'utilisateur à surmonter certaines des limites de la recherche de similarité basée sur la distance. Fournissez ces questions alternatives DANS LA MÊME LANGUE que la QUESTION ORIGINALE, en les séparant par des nouvelles lignes "\n". QUESTION ORIGINALE : {query}"""


QUERY_REWRITING_PROMPT_IT = """Il vostro compito è quello di generare {n_alt_queries} diverse versioni della domanda data dall'utente per recuperare documenti rilevanti da un database vettoriale. Generando più prospettive sulla domanda dell'utente, il vostro obiettivo è quello di aiutarlo a superare alcune delle limitazioni della ricerca per similarità basata sulla distanza. Fornire queste domande alternative NELLO STESSO LINGUAGGIO DELLA DOMANDA ORIGINALE, separate da linee nuove "\n". DOMANDA ORIGINALE: {query}"""


QUERY_STATEMENT_REWRITING_PROMPT_DE = """<anweisungen>
    <anweisung>Wenn die unten stehende <frage> gegeben ist, formuliere sie in mehreren alternativen Aussagen in einem deklarativen Tonfall um</anweisung>
    <anweisung>Jede umformulierte Aussage sollte die Bedeutung der ursprünglichen Anfrage beibehalten, sie aber auf eine etwas andere Art und Weise ausdrücken</anweisung>
    <anweisung>Schreiben Sie {n_alt_queries} deklarative Neuformulierungen in derselben Sprache wie die <frage>, getrennt durch neue „\n“-Zeilen</anweisung>
</anweisungen>.

<beispiele>
Wie ist das Wetter? -> Sagen Sie mir, wie das Wetter ist, ich möchte wissen, wie das Wetter ist.
</beispiele>.

<frage>
{query}
</frage>"""


QUERY_STATEMENT_REWRITING_PROMPT_FR = """<instructions>
    <instruction>Étant donné la <question> ci-dessous, reformulez-la en plusieurs énoncés alternatifs sur un ton déclaratif</instruction>
    <instruction>Chaque déclaration reformulée doit conserver le sens de la requête originale mais l'exprimer d'une manière légèrement différente</instruction>
    <instruction>Écrire {n_alt_queries} reformulations déclaratives dans la même langue que la <question>, séparés par de nouvelles lignes "\n"</instruction>
</instructions>

<exemples>
Quel temps fait-il ? -> Dites-moi quel temps il fait, j'aimerais connaître le temps qu'il fait.
</exemples>

<question>
{query}
</question>"""


QUERY_STATEMENT_REWRITING_PROMPT_IT = """<istruzioni>
    <istruzione> Data la <domanda> qui sotto, riformularla in diverse affermazioni alternative in tono dichiarativo</istruzione>.
    <istruzione>Ogni affermazione riformulata deve mantenere il significato della query originale, ma esprimerlo in modo leggermente diverso</istruzione>.
    <istruzione>Scrivere {n_alt_queries} riformulazioni dichiarative nello stesso linguaggio della <domanda>, separate da nuove righe "\n"</istruzione>.
</istruzioni>

<esempi>
Che tempo fa? -> Dimmi che tempo fa, vorrei sapere che tempo fa.
</esempi>

<domanda>
{query}
</domanda>
"""


CONTEXTUAL_COMPRESSION_PROMPT_DE = """Bei der folgenden FRAGE und dem KONTEXT, extrahieren Sie jeden Teil des KONTEXT *AS IS*, der für die Beantwortung der FRAGE relevant ist. Versuchen Sie, alle relevanten Links (URLs in Markdown) einzubeziehen. Wenn kein Teil des Kontextes relevant ist, geben Sie <IRRELEVANT_CONTEXT> zurück.

Denken Sie daran, dass Sie die extrahierten Teile des Kontextes *NICHT* bearbeiten dürfen.

FRAGE: {query}

KONTEXT:

{context_doc}

Extrahierte relevante Teile:"""


CONTEXTUAL_COMPRESSION_PROMPT_FR = """Pour la QUESTION et le CONTEXTE suivants, extrayez chaque partie du CONTEXTE pertinente *TELLE QUELLE* pour répondre à la QUESTION. Essayez d'inclure tous les liens (URLs en Markdown) pertinents. Si aucune partie du contexte n'est pertinente, vous renvoyez <IRRELEVANT_CONTEXT>.

N'oubliez pas que vous ne pouvez *PAS* modifier les parties extraites du contexte.

QUESTION : {query}

CONTEXTE :

{context_doc}

Parties pertinentes extraites :"""


CONTEXTUAL_COMPRESSION_PROMPT_IT = """Per la DOMANDA e il CONTESTO seguenti, estrarre qualsiasi parte del CONTESTO *COSÌ COM'E* che sia rilevante per rispondere alla DOMANDA. Cercate di includere tutti i link pertinenti (URL in Markdown). Se nessuna parte del contesto è rilevante, restituire <IRRELEVANT_CONTEXT>.

Ricordare che *NON SI DEVONO MODIFICARE* le parti estratte del contesto.

DOMANDA: {query}

CONTESTO:

{context_doc}

Parti rilevanti estratte:"""
