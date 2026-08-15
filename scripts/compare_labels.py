import json

# --- Datei einlesen ---

# Durch open öffnen wir den Datei-Inhalt. Mit .read() lesen wir den gesamten Inhalt von blind.jsonl und geben ihn zurück.

text = open("data/blind.jsonl", encoding="utf-8").read()

# Zerlegt den Text an den Umbrüchen
lines = text.splitlines()


# --- Eine Zeile in ein Dict umwandeln ---

blind = {} # Das bildet das Dict ab in dem die einzelnen Fälle gespeichert werden.

# Jede Zeile in ein Dict umwandeln und unter ihrer id ablegen,damit beide Dateien später über die id verglichen werden können.
for zeile in lines:
    fall = json.loads(zeile)
    blind[fall["id"]] = fall