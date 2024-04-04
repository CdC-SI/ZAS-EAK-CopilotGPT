-- Erstelle eine Tabelle namens 'data' für die Verwaltung der Informationen
CREATE TABLE data (
    id SERIAL PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
);

-- Erstelle eine Trigger-Funktion, um modified_at zu aktualisieren
CREATE OR REPLACE FUNCTION update_modified_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Erstelle den Trigger, der die Trigger-Funktion auslöst
CREATE TRIGGER update_data_modified_at
BEFORE UPDATE ON data
FOR EACH ROW
EXECUTE FUNCTION update_modified_at();

-- Einfügen von Chuck Norris Frage-Antwort-Paaren in die Tabelle 'data'
INSERT INTO data (url, question, answer) VALUES
('https://chucknorriswitz1', 'Wie lautet ein Chuck Norris Witz über die Schweiz?', 'Wenn Chuck Norris durch die Schweiz läuft, zittern nicht nur die Alpen, sondern auch die Uhren laufen genauer.'),
('https://chucknorriswitz2', 'Was passiert, wenn Chuck Norris einen Computer benutzt?', 'Chuck Norris braucht das Internet nicht, das Internet braucht ihn.'),
('https://chucknorriswitz3', 'Wie gewinnt Chuck Norris im Schach?', 'Chuck Norris braucht nur einen Bauern, um Schachmatt zu setzen. Der König gibt freiwillig auf.');
