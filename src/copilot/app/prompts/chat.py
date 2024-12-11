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

CHAT_TITLE_SYSTEM_PROMPT_DE = """# Aufgabe
Ihre Aufgabe ist es, einen Titel für den Chatverlauf aus der Frage des Nutzers und der Antwort des Assistenten (Antwort des Assistenten) zu generieren. Generieren Sie aus Frage und Antwort des Assistenten einen hochrangigen Titel, der die Essenz des anschliessenden Gesprächs einfängt. Die Überschrift sollte äusserst prägnant und informativ sein (MAXIMAL 4 WÖRTER) und einen kurzen Überblick über das Thema geben, der NUR auf dem Inhalt von Frage und Antwort des Assistenten beruht.

# Format der Antwort
- Der Titel MUSS auf DEUTSCH sein!
- Maximal 4 Wörter
- Nur mit dem Titel antworten!!!

# Beispiele
AHV: Berechnung der Renten
Rentenalter
Invalidenversicherung: Bedingungen für den Anspruch
Arbeitslosenversicherung: Administrative Schritte

# Antwort des Assistenten

{assistant_response}"""

CHAT_TITLE_SYSTEM_PROMPT_FR = """# Tâche
Votre tâche consiste à générer un titre pour l'historique du chat à partir de la question de l'utilisateur et de la réponse de l'assistant (Réponse de l'assistant). Générez un titre de haut niveau à partir de la Question ET Réponse de l'assistant qui capturera l'essence de la conversation qui s'ensuit. Le titre doit être extrêmement concis et informatif (MAXIMUM 4 MOTS), et donner un bref aperçu du sujet en se basant UNIQUEMENT sur le contenu de la Question et Réponse de l'assistant.

# Format de réponse
- Le titre DOIT être en FRANCAIS !
- 4 mots maximum
- Répondre uniquement avec le titre !!!

# Exemples
AVS: Calcul des rentes
Age de la retraite
Assurance invalidité: Conditions d'octroi
Assurance chômage: Démarches administratives

# Réponse de l'assistant

{assistant_response}"""

CHAT_TITLE_SYSTEM_PROMPT_IT = """# Compito
Il vostro compito è generare un titolo per la cronologia della chat a partire dalla domanda dell'utente e dalla risposta dell'assistente (Risposta dell'assistente
). Generare un titolo di alto livello dalla Domanda e dalla Risposta dell'assistente che catturi l'essenza della conversazione che ne è seguita. Il titolo deve essere estremamente conciso e informativo (MASSIMO 4 PAROLE), fornendo una breve panoramica dell'argomento basata SOLO sul contenuto della Domanda e della Risposta dell'assistente.

# Formato della risposta
- Il titolo DEVE essere in italiano!
- 4 parole al massimo
- Rispondere solo con il titolo !!!

# Esempi
AVS: Calcolo delle pensioni
Età pensionabile
Assicurazione d'invalidità: Condizioni di diritto
Assicurazione contro la disoccupazione: Procedure amministrative

# Risposta dell'assistente

{assistant_response}"""
