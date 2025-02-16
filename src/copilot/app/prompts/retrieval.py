QUERY_REWRITING_PROMPT_DE = """<kontext>
    Der Benutzer interagiert mit dem Kopiloten mit einfachen Fragen, Mehrparteienfragen, Folgefragen usw. Einfache Fragen sollten umformuliert werden, um die semantische Suche in einer Vektordatenbank zu verbessern. Mehrteilige Fragen sollten in mehrere einfache Unterfragen zerlegt werden, die pro Unterfrage eine klare Idee/ein klares Konzept enthalten. Folgefragen sollten umformuliert werden, um den Kontext des Gesprächs und die letzten Anweisungen/Informationen des Nutzers zu berücksichtigen.
</kontext>

<ziel>
    Schreiben Sie Fragen (umformuliert oder nicht), die den Kontext der Konversation und die letzten Nachrichten des Nutzers berücksichtigen, um die semantische Suche zu verbessern.
</ziel>

<anweisungen>
    <anweisung>Wenn die <frage> und der <gesprächsgeschichte> gegeben sind, formuliere Fragen, die den Kontext der Konversation und der letzten Nachrichten des Benutzers berücksichtigen</anweisung>
    <anweisung>Wenn die Frage in mehrere Unterfragen zerlegt werden kann, formuliere jede Unterfrage einzeln neu</anweisung>
    <anweisung>Jede Unterfrage sollte nur eine Idee oder ein Konzept enthalten</anweisung>
    <anweisung>Wenn die <frage> nur Präzisierungen nach einer vorherigen Frage und der Antwort des Assistenten enthält, sehen Sie sich den jüngsten <gesprächsgeschichte> an, um relevante Fragen für eine Neuformulierung zu extrahieren/abzuleiten</anweisung>
    <anweisung>Berücksichtigen Sie den gesamten neueren <gesprächsgeschichte>, der mit der <frage> in Zusammenhang steht, um die Neuformulierung zu verfeinern</anweisung>
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

QUERY_REWRITING_PROMPT_FR = """<context>
    L'utilisateur intéragit avec le copilote avec des questions simples, des questions multiparties, des questions de suivi, etc. Les questions simples doivent être reformulée pour améliorer la recherche sémantique dans une base de données vectorielle. Les questions multiparties doivent être décomposées en plusieurs sous-questions simples contenant une idée/concept clair par sous-question. Les questions de suivi doivent être reformulées pour prendre en compte le contexte de la conversation et les dernières intructions/informations de l'utilisateur.
</context>

<objectif>
    Ecrire des questions (reformulée ou non) en fonction du contexte de la conversation et des derniers messages de l'utilisateur, afin d'améliorer la recherceh sémantique.
</objectif>

<instructions>
    <instruction>Étant donné la <question> et l'<historique_de_conversation>, formulez des questions prenant en compte le contexte de la conversation et des derniers messages de l'utilisateur</instruction>
    <instruction>Quand la question peut être décomposée en plusieurs sous-questions, reformulez chaque sous-question séparément</instruction>
    <instruction>Chaque sous-question doit contenir une seule idée ou concept</instruction>
    <instruction>Si la <question> ne contient que des précisions suite à une question précédente et la réponse de l'assistant, consultez l'<historique_de_conversation> récent afin d'extraire/déduire des questions pertinentes à reformuler</instruction>
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


QUERY_REWRITING_PROMPT_IT = """<contesto>
    L'utente interagisce con il copilota con domande semplici, domande multiple, domande successive, ecc. Le domande semplici devono essere riformulate per migliorare la ricerca semantica in un database vettoriale. Le domande a più parti devono essere suddivise in diverse semplici sottodomande contenenti un'idea/concetto chiaro per ogni sottodomanda. Le domande successive devono essere riformulate per tenere conto del contesto della conversazione e delle ultime istruzioni/informazioni dell'utente.
</contesto>

<obiettivo>
    Scrivere domande (riformulate o meno) in base al contesto della conversazione e agli ultimi messaggi dell'utente, per migliorare la ricerca semantica.
</obiettivo>

<istruzioni>
    <istruzione>Data la <domanda> e la <memoria_conversazionale>, formulare domande che tengano conto del contesto della conversazione e degli ultimi messaggi dell'utente</istruzione>
    <istruzione>Quando la domanda può essere suddivisa in più sotto-domande, riformulare ogni sotto-domanda separatamente</istruzione>
    <istruzione>Ogni sotto-domanda deve contenere una singola idea o concetto</istruzione>
    <istruzione>Se la <domanda> contiene solo chiarimenti dopo una domanda precedente e la risposta dell'assistente, consultare la <memoria_conversazionale> recente per estrarre/dedurre le domande pertinenti da riformulare</istruzione>
    <istruzione>Considera tutte le <memoria_conversazionale> recenti pertinenti alla <domanda> per perfezionare la riformulazione</istruzione>
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


QUERY_STATEMENT_REWRITING_PROMPT_DE = """<kontext>
    Der Benutzer interagiert mit dem Kopiloten mit einfachen Fragen, Mehrparteienfragen, Folgefragen usw. Einfache Fragen müssen in **Anweisungen** umformuliert werden, um die semantische Suche in einer Vektordatenbank zu verbessern. Mehrteilige Fragen sollten in einfache Unteranweisungen zerlegt werden, die pro Unteranweisung eine klare Idee/ein klares Konzept enthalten. Folgefragen sollten umformuliert werden, um den Kontext des Gesprächs und die letzten Instruktionen/Informationen des Nutzers zu berücksichtigen.
</kontext>.

<ziel>
    Fragen schreiben, die unter Berücksichtigung des Kontexts der Konversation und der letzten Mitteilungen des Nutzers in Anweisungen umformuliert werden, um die semantische Suche zu verbessern.
</ziel>

<anweisungen>
    <anweisung>Wenn die <frage> und der <gesprächsgeschichte> gegeben sind, formuliere Anweisungen, die den Kontext der Konversation und die letzten Nachrichten des Benutzers berücksichtigen</anweisung>
    <anweisung>Wenn die Frage in mehrere Unteranweisungen zerlegt werden kann, formuliere jede Unteranweisung separat neu<anweisung>
    <anweisung>Jede Unteranweisung sollte nur eine Idee oder ein Konzept enthalten<anweisung>
    <anweisung>Wenn die <frage> nur Präzisierungen nach einer vorherigen Frage und der Antwort des Assistenten enthält, sehen Sie sich den jüngsten <gesprächsgeschichte> an, um relevante Fragen für eine Neuformulierung zu extrahieren/abzuleiten<anweisung>
    <anweisung>Berücksichtigen Sie den gesamten neueren <gesprächsgeschichte>, der mit der <frage> in Zusammenhang steht, um die Neuformulierung zu verfeinern<anweisung>
    <anweisung>Schreiben Sie {n_alt_queries} umformulierte Fragen als Anweisung in der gleichen Sprache wie die <frage><anweisung>
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


QUERY_STATEMENT_REWRITING_PROMPT_FR = """<context>
    L'utilisateur intéragit avec le copilote avec des questions simples, des questions multiparties, des questions de suivi, etc. Les questions simples doivent être reformulée en **instructions** pour améliorer la recherche sémantique dans une base de données vectorielle. Les questions multiparties doivent être décomposées en plusieurs sous-instructions simples contenant une idée/concept clair par sous-instruction. Les questions de suivi doivent être reformulées pour prendre en compte le contexte de la conversation et les dernières intructions/informations de l'utilisateur.
</context>

<objectif>
    Ecrire des questions reformulée en instructions en fonction du contexte de la conversation et des derniers messages de l'utilisateur, afin d'améliorer la recherceh sémantique.
</objectif>

<instructions>
    <instruction>Étant donné la <question> et l'<historique_de_conversation>, formulez des instructions prenant en compte le contexte de la conversation et des derniers messages de l'utilisateur</instruction>
    <instruction>Quand la question peut être décomposée en plusieurs sous-instructions, reformulez chaque sous-instruction séparément</instruction>
    <instruction>Chaque sous-instruction doit contenir une seule idée ou concept</instruction>
    <instruction>Si la <question> ne contient que des précisions suite à une question précédente et la réponse de l'assistant, consultez l'<historique_de_conversation> récent afin d'extraire/déduire des questions pertinentes à reformuler</instruction>
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


QUERY_STATEMENT_REWRITING_PROMPT_IT = """<contesto>
    L'utente interagisce con il copilota con domande semplici, domande multiple, domande di follow-up, ecc. Le domande semplici devono essere riformulate in **istruzioni** per migliorare la ricerca semantica in un database vettoriale. Le domande in più parti devono essere suddivise in diverse semplici sottoistruzioni contenenti un'idea/concetto chiaro per ogni sottoistruzione. Le domande successive devono essere riformulate per tenere conto del contesto della conversazione e delle ultime informazioni dell'utente.
</contesto>

<obiettivo>
    Scrivere domande riformulate in istruzioni in base al contesto della conversazione e agli ultimi messaggi dell'utente, per migliorare la ricerca semantica.
</obiettivo>

<istruzioni>
    <istruzione>Data la <domanda> e la <memoria_conversazionale>, formulare istruzioni che tengano conto del contesto della conversazione e dei messaggi più recenti dell'utente</istruzione>
    <istruzione>Quando la domanda può essere suddivisa in più sottoistruzioni, riformulare ogni sottoistruzione separatamente</istruzione>
    <istruzione>Ogni sottoistruzione deve contenere una singola idea o concetto</istruzione>
    <istruzione>Se la <domanda> contiene solo chiarimenti dopo una domanda precedente e la risposta della procedura guidata, consultare la <memoria_conversazionale> recente per estrarre/ridurre le domande pertinenti da riformulare</istruzione>
    <istruzione>Considerare tutta la <memoria_conversazionale> recente e pertinente alla <domanda> per perfezionare la riformulazione</istruzione>
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
