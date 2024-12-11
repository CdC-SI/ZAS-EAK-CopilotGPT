SUMMARIZE_COMMAND_PROMPT_DE = """Ihre Aufgabe besteht darin, eine Zusammenfassung des TEXTES zu erstellen, der eine Konversation (Frage und Antwort zwischen Benutzer und Assistent) enthält. Lesen Sie den TEXT aufmerksam durch und fassen Sie die wichtigsten Punkte der gegebenen Antworten (des Assistenten) im angegebenen STIL zusammen. Die Zusammenfassung sollte {style} und informativ sein, wobei Sie nur die wichtigsten Informationen berücksichtigen. Vermeiden Sie es, irrelevante Details zu erwähnen.

Sie müssen sich auf {mode} des TEXT konzentrieren.

STIL: {style}
TEXT:

{input_text}

Die Zusammenfassung muss auf DEUTSCH verfasst sein!

ZUSAMMENFASSUNG:"""

SUMMARIZE_COMMAND_PROMPT_FR = """Votre tâche consiste à générer un résumé du TEXTE contenant une conversation (question-réponse entre user-assistant). Lisez attentivement le TEXTE et résumez les points les plus importants des réponses fournies (de l'assistant) dans le STYLE spécifé. Le résumé doit être {style} et informatif, en ne prenant en compte que les informations les plus importantes. Évitez de mentionner des détails non pertinents.

Vous devez vous concentrer sur {mode} du TEXTE.

STYLE: {style}
TEXTE :

{input_text}

Le résumé doit être rédigé en FRANCAIS !

RÉSUMÉ : """

SUMMARIZE_COMMAND_PROMPT_IT = """Il vostro compito è generare un riassunto del TESTO contenente una conversazione (domanda-risposta tra utente-assistente). Leggere attentamente il TESTO e riassumere i punti più importanti delle risposte fornite (dall'assistente) nello STILE specificato. Il riassunto deve essere {style} e informativo, tenendo conto solo delle informazioni più importanti. Evitare di menzionare dettagli irrilevanti.

È necessario concentrarsi {mode} del TESTO.

STILE: {style}
TESTO:

{input_text}

Il riassunto deve essere scritto in ITALIANO!

RIASSUNTO:"""
