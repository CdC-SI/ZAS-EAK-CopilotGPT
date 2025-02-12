QUERY_REWRITING_PROMPT_DE = """<anweisungen>
    <anweisung>Wenn die unten stehende <frage> gegeben ist, formuliere sie auf mehrere verschiedene Arten um</anweisung>
    <anweisung>Wenn die Frage in mehrere Unterfragen zerlegt werden kann, formuliere jede Unterfrage separat um</anweisung>
    <anweisung>Berücksichtigen Sie die gesamte <gesprächsgeschichte>, die kürzlich stattgefunden hat und mit der <frage> in Zusammenhang steht, um die Neuformulierung zu verfeinern</anweisung>
    <anweisung>Schreiben Sie {n_alt_queries} umformulierte Fragen in der gleichen Sprache wie die <frage></anweisung>
</anweisungen>

<format_der_antwort>.
QueryReformulation(
    reformulations: List[str] # Liste der Neuformulierungen der <frage>.
)
</format_der_antwort>.

<beispiele>
Wie erhalte ich einen Auszug aus dem individuellen Konto? -> ["Erkläre mir, wie ich einen Auszug aus dem individuellen Konto erhalte" usw.].
Was bedeutet das flexible Rentenalter? -> ["Was bedeutet das flexible Rentenalter?", usw.]
Erkläre mir das Splitting und wie es funktioniert? -> ["Was ist das Splitting?", "Wie funktioniert das Splitting?", usw.].
Wie bekomme ich einen Auszug aus dem individuellen Konto und wo finde ich Informationen? -> ["Erkläre mir, wie man einen Auszug aus dem individuellen Konto erhält", "Wo finde ich Informationen über den Auszug aus dem individuellen Konto?", usw.].
</beispiele>

<gesprächsgeschichte>
{conversational_memory}
</gesprächsgeschichte>

<frage>
{query}
</frage>"""

QUERY_REWRITING_PROMPT_FR = """<instructions>
    <instruction>Étant donné la <question> ci-dessous, reformulez-la de plusieurs manières distinctes</instruction>
    <instruction>Quand la question peut être décomposée en plusieurs sous-questions, reformulez chaque sous-question séparément</instruction>
    <instruction>Prenez en compte tout l'<historique_de_conversation> récent et en rapport avec la <question> afin de raffiner la reformulation</instruction>
    <instruction>Écrire {n_alt_queries} questions reformulées dans la même langue que la <question></instruction>
</instructions>

<format_de_réponse>
QueryReformulation(
    reformulations: List[str] # Liste des reformulations de la <question>
)
</format_de_réponse>

<exemples>
Comment obtenir un extrait du compte individuel ? -> ["Explique moi comment obtenir un extrait du compte individuel", etc.]
Que signifie l'âge de la retraite flexible ? -> ["Qu'est-ce que l'âge de la retraite flexible ?", etc.]
Explique moi le splitting et comment il fonctionne ? -> ["Qu'est-ce que le splitting ?", "Comment le splitting fonctionne-t-il ?", etc.]
Comment obtenir un extrait du compte individuel et ou trouver des informations ? -> ["Explique moi comment obtenir un extrait du compte individuel", "Où trouver des informations sur l'extrait du compte individuel ?", etc.]
</exemples>

<historique_de_conversation>
{conversational_memory}
</historique_de_conversation>

<question>
{query}
</question>"""


QUERY_REWRITING_PROMPT_IT = """<istruzioni>
    <istruzione> Data la <domanda> qui sotto, riformularla in diversi modi distinti</istruzione>
    <istruzione>Quando la domanda può essere scomposta in diverse sotto-domande, riformulare ogni sotto-domanda separatamente</istruzione>
    <istruzione>Tenere conto di tutte le <memoria_conversazionale> recenti e relative alla <domanda> per perfezionare la riformulazione</istruzione>
    <istruzione>Scrivere {n_alt_queries} domande riformulate nella stessa lingua della <domanda></istruzione>
</istruzioni>

<formato_di_risposta>
QueryReformulation(
    reformulations: List[str] # List di riformulazioni della <domanda>.
)
</formato_di_risposta>

<esempi>
Come si ottiene un estratto conto individuale? -> ["Spiegami come ottenere un estratto conto individuale", ecc.]
Cosa significa età pensionabile flessibile? -> ["Che cos'è l'età pensionabile flessibile?", ecc.]
Può spiegare come funziona lo splitting? -> ["Cos'è lo splitting?", "Come funziona lo splitting?", ecc.]
Come posso ottenere un estratto conto individuale e dove posso trovare informazioni? -> ["Spiegami come ottenere un estratto conto individuale", "Dove posso trovare informazioni sull'estratto conto individuale?", ecc.]
</esempi>

<memoria_conversazionale>
{conversational_memory}
</memoria_conversazionale>

<domanda>
{query}
</domanda>"""


QUERY_STATEMENT_REWRITING_PROMPT_DE = """<anweisungen>
    <anweisung>Wenn die unten stehende <frage> gegeben ist, formuliere sie in mehrere Aussagen in Form einer Anweisung um</anweisung>
    <anweisung>Wenn die Frage in mehrere Unterfragen zerlegt werden kann, formuliere jede Unterfrage einzeln um</anweisung>
    <anweisung>Berücksichtigen Sie die gesamte <gesprächsgeschichte>, die kürzlich stattgefunden hat und mit der <frage> in Zusammenhang steht, um die Neuformulierung zu verfeinern</anweisung>
    <anweisung>Schreiben Sie {n_alt_queries} umformulierte Fragen als Anweisung in der gleichen Sprache wie die <frage></anweisung>
</anweisungen>

<format_der_antwort>
QueryReformulation(
    reformulations: List[str] # Liste der Umformulierungen in Form von Anweisungen der <frage>.
)
<format_der_antwort>

<beispiele>
Wie erhalte ich einen Auszug aus dem individuellen Konto? -> ["Erkläre mir, wie ich einen Auszug aus dem individuellen Konto erhalte", usw.].
Was bedeutet das Splitting? -> ["Das Splitting erklärt", usw.].
Was bedeutet flexibles Rentenalter? -> ["flexibles Rentenalter", etc.].
Was ist das Splitting und wie funktioniert es? -> ["Das Splitting erklärt", "Funktionsweise des Splittings", etc.]
Was ändert sich mit avs21 und wann ist die Reform in Kraft getreten? -> ["Änderungen mit avs21", "Inkrafttreten von avs21", usw.]
</beispiele>

<gesprächsgeschichte>
{conversational_memory}
</gesprächsgeschichte>

<frage>
{query}
</frage>"""


QUERY_STATEMENT_REWRITING_PROMPT_FR = """<instructions>
    <instruction>Étant donné la <question> ci-dessous, reformulez-la en plusieurs énoncés sous forme d'instruction</instruction>
    <instruction>Quand la question peut être décomposée en plusieurs sous-questions, reformulez chaque sous-question séparément</instruction>
    <instruction>Prenez en compte tout l'<historique_de_conversation> récent et en rapport avec la <question> afin de raffiner la reformulation</instruction>
    <instruction>Écrire {n_alt_queries} questions reformulées sous forme d'instruction dans la même langue que la <question></instruction>
</instructions>

<format_de_réponse>
QueryReformulation(
    reformulations: List[str] # Liste des reformulations sous forme d'instruction de la <question>
)
</format_de_réponse>

<exemples>
Comment obtenir un extrait du compte individuel ? -> ["Explique moi comment obtenir un extrait du compte individuel", etc.]
Que signifie le splitting ? -> ["Le splitting expliqué", etc.]
Que signifie l'âge de la retraite flexible ? -> ["age de la retraite flexible", etc.]
Qu'est ce que le splitting et comment fonctionne t'il ? -> ["Le splitting expliqué", "Fonctionnement du splitting", etc.]
Qu'est-ce qui change avec avs21 et quand la réforme est-elle entrée en vigueur ? -> ["Changements avec avs21", "Entrée en vigueur d'AVS21", etc.]
</exemples>

<historique_de_conversation>
{conversational_memory}
</historique_de_conversation>

<question>
{query}
</question>"""


QUERY_STATEMENT_REWRITING_PROMPT_IT = """<istruzioni>
    <istruzione> Data la <domanda> qui sotto, riformularla in diverse affermazioni sotto forma di istruzione</istruzione>
    <istruzione>Quando la domanda può essere scomposta in diverse sotto-domande, riformulare ogni sotto-domanda separatamente</istruzione>
    <istruzione>Tenere conto di tutte le <memoria_conversazionale> recenti e relative alla <domanda> per perfezionare la riformulazione</istruzione>
    <istruzione>Scrivere {n_alt_queries} domande riformulate come istruzione nella stessa lingua della <domanda></istruzione>
</istruzioni>

<formato_di_risposta>
Riformulazione di domande(
    reformulations: List[str] # List di riformulazioni in forma di istruzione della <domanda>
)
</formato_di_risposta>

<esempi>
Come si ottiene un estratto conto individuale? -> ["Spiegami come ottenere un estratto conto individuale", ecc.]
Che cosa significa splittare? -> ["Spiegazione della scissione", ecc.]
Che cos'è l'età pensionabile flessibile? -> ["Età pensionabile flessibile", etc.]
Cos'è e come funziona lo splitting? -> ["Lo splitting spiegato", "Come funziona lo splitting", ecc.]
Cosa cambia con l'avs21 e quando è entrata in vigore la riforma? -> ["Cambiamenti con l'avs21", "Entrata in vigore dell'AVS21", ecc.]
</esempi>.

<memoria_conversazionale>
{conversational_memory}
</memoria_conversazionale>

<domanda>
{query}
</domanda>"""


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
