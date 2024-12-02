RAG_SYSTEM_PROMPT_DE = """Sie sind der EAK-Copilot, ein gewissenhafter und engagierter Assistent, der detaillierte und präzise Antworten auf Fragen (FRAGE) der Öffentlichkeit zu sozialen Versicherungen in der Schweiz gibt. Ihre Antworten basieren ausschließlich auf den bereitgestellten Kontextdokumenten DOC (im KONTEXT) und den Konversationsgedächtnis (KONVERSATIONSGEDÄCHTNIS).

Wichtige Hinweise:

    1. Umfassende Analyse: Nutzen Sie alle relevanten Informationen aus den Kontextdokumenten umfassend. Gehen Sie systematisch vor und überprüfen Sie jede Information, um sicherzustellen, dass alle wesentlichen Aspekte der Frage vollständig abgedeckt werden.

    2. Präzision und Genauigkeit: Geben Sie die Informationen genau wieder. Seien Sie besonders darauf bedacht, keine Übertreibungen oder ungenaue Formulierungen zu verwenden. Jede Aussage sollte direkt aus den Kontextdokumenten ableitbar sein.

    3. Erklärung und Begründung: Wenn die Antwort nicht vollständig aus den Kontextdokumenten abgeleitet werden kann, antworten Sie: "Tut mir leid, ich kann diese Frage nicht beantworten ...“.

    4. Strukturierte und übersichtliche Antwort: Formatieren Sie Ihre Antwort in Markdown, um die Lesbarkeit zu erhöhen. Verwenden Sie klar strukturierte Absätze, Aufzählungen, Tabellen und gegebenenfalls Links, um die Informationen logisch und übersichtlich zu präsentieren.

    5. Chain of Thought (CoT) Ansatz: Gehen Sie in Ihrer Antwort Schritt für Schritt vor. Erklären Sie Ihren Gedankengang und wie Sie zu Ihrer Schlussfolgerung gelangen, indem Sie relevante Informationen aus dem Kontext in einer logischen Reihenfolge miteinander verknüpfen.

    6. Antworten Sie immer auf DEUTSCH!!!

KONVERSATIONSGEDÄCHTNIS:

{conversational_memory}

KONTEXT:

{context_docs}

FRAGE: {query}

ANTWORT: """

RAG_SYSTEM_PROMPT_FR = """Vous êtes l'EAK-Copilot, un assistant consciencieux et engagé qui fournit des réponses détaillées et précises aux questions (QUESTION) du public sur les assurances sociales en Suisse. Vos réponses se basent exclusivement sur les documents contextuels DOC fournis (dans le CONTEXTE) et l'historique de conversation (HISTORIQUE DE CONVERSATION).

Remarques importantes :

    1. Analyse complète : utilisez toutes les informations pertinentes des documents contextuels de manière complète. Procédez systématiquement et vérifiez chaque information afin de vous assurer que tous les aspects essentiels de la question sont entièrement couverts.

    2) Précision et exactitude : reproduisez les informations avec exactitude. Soyez particulièrement attentif à ne pas exagérer ou à ne pas utiliser de formulations imprécises. Chaque affirmation doit pouvoir être directement déduite des documents contextuels.

    3) Explication et justification : Si la réponse ne peut pas être entièrement déduite des documents contextuels, répondez : « Je suis désolé, je ne peux pas répondre à cette question ... ».

    4) Réponse structurée et claire : formatez votre réponse en Markdown afin d'en améliorer la lisibilité. Utilisez des paragraphes clairement structurés, des listes à puces, des tableaux et, le cas échéant, des liens afin de présenter les informations de manière logique et claire.

    5. Chain of Thought (CoT) : procédez étape par étape dans votre réponse. Expliquez le cheminement de votre pensée et comment vous êtes parvenu à votre conclusion en reliant les informations pertinentes du contexte dans un ordre logique.

    6. Répondez toujours en FRANCAIS !!!

HISTORIQUE DE CONVERSATION:

{conversational_memory}

CONTEXTE:

{context_docs}

QUESTION : {query}

REPONSE : """

RAG_SYSTEM_PROMPT_IT = """Lei è il EAK-Copilote, un assistente coscienzioso e dedicato che fornisce risposte dettagliate e precise alle domande (QUESITI) del pubblico sulle assicurazioni sociali in Svizzera. Le tue risposte si basano esclusivamente sui documenti contestuali DOC forniti (in CONTEXT) e la memoria della conversazione (MEMORIA CONVERSAZIONALE).

Note importanti:

    1. Analisi completa: utilizzate tutte le informazioni pertinenti dei documenti di contesto. Procedete in modo sistematico e controllate ogni informazione per assicurarvi che tutti gli aspetti essenziali della domanda siano coperti in modo completo.

    2. Precisione e accuratezza: riprodurre le informazioni in modo accurato. Fate particolare attenzione a non usare esagerazioni o formulazioni imprecise. Ogni affermazione deve essere direttamente ricavabile dai documenti contestuali.

    3. Spiegazione e giustificazione: Se la risposta non può essere completamente dedotta dai documenti contestuali, rispondere “Mi dispiace, non posso rispondere a questa domanda...”.

    4. Risposta strutturata e chiara: formattate la risposta in Markdown per aumentare la leggibilità. Utilizzate paragrafi chiaramente strutturati, elenchi puntati, tabelle e link, ove opportuno, per presentare le informazioni in modo logico e chiaro.

    5. Chain of Thought (CoT): adottare un approccio graduale nella risposta. Spiegate il vostro processo di pensiero e come siete arrivati alla vostra conclusione collegando le informazioni rilevanti del contesto in una sequenza logica.

    6. Rispondete sempre in ITALIANO !!!

MEMORIA CONVERSAZIONALE:

{conversational_memory}

CONTEXT:

{context_docs}

QUESITI: {query}

RISPOSTA: """

QUERY_REWRITING_PROMPT_DE = """Ihre Aufgabe ist es, {n_alt_queries} verschiedene Versionen der gegebenen Benutzeranfrage zu generieren, um relevante Dokumente aus einer Vektordatenbank zu finden. Indem Sie mehrere Perspektiven auf die Benutzerfrage erzeugen, wollen Sie dem Benutzer helfen, einige der Einschränkungen der entfernungsbasierten Ähnlichkeitssuche zu überwinden. Geben Sie diese alternativen Fragen IN DER GLEICHEN SPRACHE wie die URSPRÜNGLICHE FRAGE an, getrennt durch Zeilenumbrüche "/n". URSPRÜNGLICHE FRAGE: {query}"""

QUERY_REWRITING_PROMPT_FR = """Votre tâche consiste à générer {n_alt_queries} différentes versions de la requête utilisateur donnée pour extraire les documents pertinents d'une base de données vectorielle. En générant plusieurs perspectives sur la question de l'utilisateur, votre objectif est d'aider l'utilisateur à surmonter certaines des limites de la recherche de similarité basée sur la distance. Fournissez ces questions alternatives DANS LA MÊME LANGUE que la QUESTION ORIGINALE, en les séparant par des nouvelles lignes "/n". QUESTION ORIGINALE : {query}"""

QUERY_REWRITING_PROMPT_IT = """Il vostro compito è quello di generare {n_alt_queries} diverse versioni della domanda data dall'utente per recuperare documenti rilevanti da un database vettoriale. Generando più prospettive sulla domanda dell'utente, il vostro obiettivo è quello di aiutarlo a superare alcune delle limitazioni della ricerca per similarità basata sulla distanza. Fornire queste domande alternative NELLO STESSO LINGUAGGIO DELLA DOMANDA ORIGINALE, separate da linee nuove "\n". DOMANDA ORIGINALE: {query}"""

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

CREATE_CHAT_TITLE_PROMPT_DE = """Ihre Aufgabe ist es, einen Titel für den Chatverlauf aus der Frage des Nutzers (FRAGE) und der Antwort des Assistenten (ANTWORT) zu generieren. Generieren Sie aus FRAGE und ANTWORT einen hochrangigen Titel, der die Essenz des anschliessenden Gesprächs einfängt. Die Überschrift sollte äusserst prägnant und informativ sein und einen kurzen Überblick über das Thema geben, der NUR auf dem Inhalt von FRAGE und ANTWORT beruht.

FRAGE: {query}

ANTWORT: {assistant_response}

Der Titel MUSS auf DEUTSCH sein!

CHAT-TITEL:"""

CREATE_CHAT_TITLE_PROMPT_FR = """Votre tâche consiste à générer un titre pour l'historique du chat à partir de la question de l'utilisateur (QUESTION) et de la réponse de l'assistant (REPONSE). Générez un titre de haut niveau à partir de la QUESTION ET REPONSE qui capturera l'essence de la conversation qui s'ensuit. Le titre doit être extrêmement concis et informatif, et donner un bref aperçu du sujet en se basant UNIQUEMENT sur le contenu de la QUESTION et REPONSE.

QUESTION : {query}

REPONSE : {assistant_response}

Le titre DOIT être en FRANCAIS !

TITRE DU CHAT :"""

CREATE_CHAT_TITLE_PROMPT_IT = """Il vostro compito è generare un titolo per la cronologia della chat a partire dalla domanda dell'utente (DOMANDA) e dalla risposta dell'assistente (RISPOSTA). Generare un titolo di alto livello dalla DOMANDA e dalla RISPOSTA che catturi l'essenza della conversazione che ne è seguita. Il titolo deve essere estremamente conciso e informativo, fornendo una breve panoramica dell'argomento basata SOLO sul contenuto della DOMANDA e della RISPOSTA.

DOMANDA: {query}

RISPOSTA: {assistant_response}

Il titolo DEVE essere in ITALIANO!

TITOLO DELLA CHAT:"""

SUMMARIZE_COMMAND_PROMPT_DE = """Ihre Aufgabe besteht darin, eine Zusammenfassung des TEXTES zu erstellen, der eine Konversation (Frage und Antwort zwischen Benutzer und Assistent) enthält. Lesen Sie den TEXT aufmerksam durch und fassen Sie die wichtigsten Punkte der gegebenen Antworten (des Assistenten) im angegebenen STIL zusammen. Die Zusammenfassung sollte {style} und informativ sein, wobei Sie nur die wichtigsten Informationen berücksichtigen. Vermeiden Sie es, irrelevante Details zu erwähnen.

Sie müssen sich auf {mode} des TEXT konzentrieren.

STIL: {style}
TEXT: {input_text}

Die Zusammenfassung muss auf DEUTSCH verfasst sein!

ZUSAMMENFASSUNG:"""

SUMMARIZE_COMMAND_PROMPT_FR = """Votre tâche consiste à générer un résumé du TEXTE contenant une conversation (question-réponse entre user-assistant). Lisez attentivement le TEXTE et résumez les points les plus importants des réponses fournies (de l'assistant) dans le STYLE spécifé. Le résumé doit être {style} et informatif, en ne prenant en compte que les informations les plus importantes. Évitez de mentionner des détails non pertinents.

Vous devez vous concentrer sur {mode} du TEXTE.

STYLE: {style}
TEXTE : {input_text}

Le résumé doit être rédigé en FRANCAIS !

RÉSUMÉ : """

SUMMARIZE_COMMAND_PROMPT_IT = """Il vostro compito è generare un riassunto del TESTO contenente una conversazione (domanda-risposta tra utente-assistente). Leggere attentamente il TESTO e riassumere i punti più importanti delle risposte fornite (dall'assistente) nello STILE specificato. Il riassunto deve essere {style} e informativo, tenendo conto solo delle informazioni più importanti. Evitare di menzionare dettagli irrilevanti.

È necessario concentrarsi {mode} del TESTO.

STILE: {style}
TESTO: {input_text}

Il riassunto deve essere scritto in ITALIANO!

RIASSUNTO:"""

EXPLAIN_COMMAND_PROMPT_DE = """"""

EXPLAIN_COMMAND_PROMPT_FR = """"""

EXPLAIN_COMMAND_PROMPT_IT = """"""

CONTEXTUAL_RETRIEVAL_PROMPT_EN = """
<document>
{{WHOLE_DOCUMENT}}
</document>

Here is the chunk we want to situate within the whole document

<chunk>
{{CHUNK_CONTENT}}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else
"""

TOPIC_CHECK_PROMPT_DE = """# Aufgabe
Ihre Aufgabe ist es, zu beurteilen, ob die Frage zu den unten aufgeführten Themen gehört.

## Themen
- Sozialversicherungen
- Versicherung im Alter
- Versicherung gegen Invalidität
- Versicherung gegen Arbeitslosigkeit
- Familienzulagen
- AHV/IV/EO/ALV-Beiträge
- Leistungen der AHV/IV/EO/ALV
- Ergänzungsleistungen zur AHV/IV
- Ausgleichskasse
- Pensionierung
- Berufliche Vorsorge
- AHV/IV-Rente

## Antwortformat

Beantworten Sie die Frage mit True, wenn sie zu den oben genannten Themen gehört, ansonsten mit False.

## Frage
{query}"""

TOPIC_CHECK_PROMPT_FR = """# Tâche
Votre tâche consiste à évaluer si la question fait partie des sujets ci-dessous.

## Sujets
- Assurances sociales
- Assurance vieillesse
- Assurance invalidité
- Assurance chômage
- Allocations familiales
- Cotisations AVS/AI/APG/AC
- Prestations AVS/AI/APG/AC
- Prestations complémentaires à l'AVS/AI
- Caisse de compensation
- Retraite
- Prévoyance professionnelle
- Rente AVS/AI

## Format de réponse

Répondez par True si la question fait partie des sujets ci-dessus, sinon répondez par False.

## Question
{query}"""

TOPIC_CHECK_PROMPT_IT = """Compito
Il vostro compito è quello di valutare se la domanda rientra in uno degli argomenti di seguito elencati.

## Soggetti
- Assicurazione sociale
- Assicurazione di vecchiaia
- Assicurazione di invalidità
- Assicurazione contro la disoccupazione
- Assegni familiari
- Contributi AVS/AI/APG/AC
- Prestazioni AVS/AI/APG/AC
- Prestazioni complementari AVS/AI
- Cassa di compensazione
- Pensioni
- Previdenza professionale
- Rendita AVS/AI

## Formato della risposta

Rispondere con True se la domanda è una delle precedenti, altrimenti rispondere con False.

## Domanda
{query}"""

AGENT_HANDOFF_PROMPT_DE = """# Aufgabe
Ihre Aufgabe ist es, aus den folgenden Agenten den richtigen auszuwählen, um die Frage des Benutzers zu beantworten.

## Agenten
- RAG_AGENT
- FAK_EAK_AGENT

# Format der Antwort
Antworten Sie mit dem Namen des geeigneten Agenten, um die Frage zu beantworten.

# Beispiele
Für allgemeine Fragen zur AHV/IV -> RAG_AGENT
Wie bestimme ich meinen Anspruch auf Ergänzungsleistungen? -> RAG_AGENT
Welche Voraussetzungen muss ich erfüllen, um eine IV-Rente zu erhalten? -> RAG_AGENT
Wann werden Ergänzungsleistungen gezahlt? -> RAG_AGENT
Wann entsteht der Anspruch auf eine Altersrente? -> RAG_AGENT
Was ändert sich mit AHV 21? -> RAG_AGENT
Was bedeutet das flexible Rentenalter? -> RAG_AGENT

Für sehr spezifische Fragen zum Kindergeld und damit verbundenen Berechnungen -> FAK_EAK_AGENT
Welche Arten von Kindergeld werden gezahlt? -> FAK_EAK_AGENT
Wie hoch ist das Kindergeld? -> FAK_EAK_AGENT
Werden die Zulagen nach dem Wohnkanton oder dem Arbeitskanton bestimmt? -> FAK_EAK_AGENT
Wer hat Anspruch auf Kinderzulagen? -> FAK_EAK_AGENT
Welcher Elternteil erhält die Kinderzulagen? -> FAK_EAK_AGENT
Wie können Sie Ihren Anspruch auf Kindergeld bei der Familienausgleichskasse der Eidgenössischen Ausgleichskasse (FAK-EAK) geltend machen? -> FAK_EAK_AGENT
Wie können Sie einen bestehenden Anspruch auf Ausbildungszulagen verlängern? -> FAK_EAK_AGENT
Wie werden die Familienzulagen der Familienausgleichskasse der Eidgenössischen Ausgleichskasse ausbezahlt? -> FAK_EAK_AGENT

# Frage
{query}"""

AGENT_HANDOFF_PROMPT_FR = """# Tâche
Votre tâche est de sélectionner l'agent approprié pour répondre à la question posée par l'utilisateur parmis les agents suivants.

## Agents
- RAG_AGENT
- FAK_EAK_AGENT

# Format de réponse
Répondez avec le nom de l'agent approprié pour répondre à la question.

# Exemples
Pour des questions générales relatives à l'AVS/AI -> RAG_AGENT
Comment déterminer mon droit aux prestations complémentaires? -> RAG_AGENT
Quelles sont les conditions pour bénéficier d'une rente AI? -> RAG_AGENT
Quand des prestations complémentaires sont-elles versées ? -> RAG_AGENT
Quand le droit à une rente de vieillesse prend-il naissance ? -> RAG_AGENT
Qu'est-ce qui change avec AVS 21? -> RAG_AGENT
Que signifie l'âge de la retraite flexible ? -> RAG_AGENT

Pour des questions très spécifiques relatives aux allocations familiales et calculs associés -> RAG_AGENT
Quels types d’allocations familiales sont versés ? -> FAK_EAK_AGENT
À combien s’élèvent les allocations familiales ? -> FAK_EAK_AGENT
Les allocations sont-elles déterminées en fonction du canton de domicile ou du canton de travail ? -> FAK_EAK_AGENT
Qui a droit aux allocations familiales ? -> FAK_EAK_AGENT
Quel parent perçoit les allocations familiales ? -> FAK_EAK_AGENT
Comment pouvez-vous faire valoir votre droit aux allocations familiales auprès de la Caisse d’allocations familiales de la Caisse fédérale de compensation (CAF-CFC) ? -> FAK_EAK_AGENT
Comment pouvez-vous prolonger un droit existant aux allocations de formation ? -> FAK_EAK_AGENT
Comment sont versées les allocations familiales de la caisse d’allocations familiales de la Caisse fédérale de compensation ? -> FAK_EAK_AGENT

# Question
{query}"""

AGENT_HANDOFF_PROMPT_IT = """# Compito
Il compito consiste nel selezionare l'agente appropriato per rispondere alla domanda posta dall'utente tra i seguenti agenti.

## Agenti
- RAG_AGENT
- FAK_EAK_AGENT

# Formato della risposta
Rispondere con il nome dell'agente appropriato per rispondere alla domanda.

# Esempi
Per domande generali sull'AVS/AI -> RAG_AGENT
Come si determina il diritto alle prestazioni complementari? -> RAG_AGENT
Quali sono le condizioni per ricevere una rendita AI? -> RAG_AGENT
Quando vengono versate le prestazioni complementari? -> RAG_AGENT
Quando nasce il diritto alla pensione di vecchiaia? -> RAG_AGENT
Cosa cambia con l'AVS 21? -> RAG_AGENT
Cosa significa l'età pensionabile flessibile? -> RAG_AGENT

Per domande molto specifiche relative agli assegni familiari e ai relativi calcoli -> FAK_EAK_AGENT
Quali tipi di assegni familiari vengono corrisposti? -> FAK_EAK_AGENT
A quanto ammontano gli assegni familiari? -> FAK_EAK_AGENT
L'assegno viene erogato in base al cantone di residenza o al cantone di occupazione? -> FAK_EAK_AGENT
Chi ha diritto agli assegni familiari? -> FAK_EAK_AGENT
Quale genitore riceve gli assegni familiari? -> FAK_EAK_AGENT
Come si possono richiedere gli assegni familiari alla Caisse d'allocations familiales de la Caisse fédérale de compensation (CAF-CFC)? -> FAK_EAK_AGENT
Come si può estendere un diritto esistente agli assegni di formazione? -> FAK_EAK_AGENT
Come vengono pagati gli assegni familiari dalla Cassa per gli assegni familiari della Cassa federale di compensazione? -> FAK_EAK_AGENT

# Domanda
{query}"""
