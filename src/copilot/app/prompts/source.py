SOURCE_DESCRIPTION_SYSTEM_PROMPT_DE = """<aufgabe>
Bitte geben Sie eine hochrangige Zusammenfassung des gesamten Inhalts der betreffenden <dokumente>.
Konzentrieren Sie sich auf die allgemeinen Themen, Schlüsselthemen und das Hauptziel, ohne in spezifische Abschnitte, Artikelnummern oder detaillierte Unterabschnitte abzutauchen. Achten Sie darauf, dass Ihre Zusammenfassung die Essenz der <dokumente> kurz und präzise erfasst.
Verfassen Sie eine Beschreibung von 5-10 Sätzen in der Sprache der <dokumente>.
Sie können auch <source_name> zu Rate ziehen, um Ihre Beschreibung ggf. zu verfeinern.
</aufgabe>.

<documente>
{docs}
</documente>.

<source_name>
{source_name}
</source_name>"""

SOURCE_DESCRIPTION_SYSTEM_PROMPT_FR = """<instructions>
    <instruction>Rédigez un résumé de haut niveau capturant l'ensemble du contenu des <documents> </instruction>
    <instruction>Concentrez-vous sur les thèmes généraux, les sujets clés et l'objectif principal sans plonger dans des sections spécifiques, des numéros d'articles ou des sous-sections détaillées. Veillez à ce que votre résumé capture l'essence des <documents> de manière concise et précise</instruction>
    <instruction>Rédigez une description de 5-10 phrases dans la langue des <documents></instruction>
    <instruction>Vous pouvez également consulter la <source> des <documents> pour affiner votre description si nécessaire</instruction>
    <instruction>Le but final est de décrire l'information contenue dans les <documents> appartenants à la <source></instruction>
</instructions>

<documents>
{docs}
</documents>

<source>
{source_name}
</source>"""

SOURCE_DESCRIPTION_SYSTEM_PROMPT_IT = """<compito>
Fornite un riassunto di alto livello dell'intero contenuto dei <documenti> in questione.
Concentratevi sui temi generali, sugli argomenti chiave e sullo scopo principale senza addentrarvi in sezioni specifiche, numeri di articoli o sottosezioni dettagliate.
Assicuratevi che il vostro riassunto catturi l'essenza dei <documenti> in modo conciso e accurato.
Scrivete una descrizione di 5-10 frasi nella lingua dei <documenti>.
Potete anche consultare <source_name> per perfezionare la descrizione, se necessario.
<compito>

<documenti>
{documenti}
</documenti>

<source_name>
{source_name}
</source_name>"""
