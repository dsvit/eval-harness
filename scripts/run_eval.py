# Runner für den Eval-Harness.
#
# Liest die Kundennachrichten aus data/dev.jsonl, setzt jede in den Prompt aus
# prompts/triage_v1.md ein, schickt sie ans Modell und schreibt die Antworten
# nach runs/.
#
# Nur der input geht ans Modell -- expected bleibt zurück und wird erst später
# vom Grader zum Abgleich benutzt.
#
# Der Runner interpretiert nichts. Gespeichert wird die Rohantwort als Text,
# auch wenn sie kaputt ist. Das Auswerten ist Sache des Graders -- so muss ein
# Fehler in der Parse-Logik nie einen Modelllauf wiederholen.
#
# TODO: Fehlerbehandlung ergänzen, sobald hier eine Fern-API statt Ollama läuft.
# Lokal fällt ein Aufruf praktisch nur beim ersten Fall aus (Ollama nicht
# gestartet, Speicher zu klein). Bei einer bezahlten API kommen Rate Limits,
# Zeitüberschreitungen und kurzzeitige Serverfehler dazu -- die treffen einzelne
# Fälle mitten im Lauf. Dann den Aufruf in try/except fassen und den Fehler als
# Antwort festhalten, statt den ganzen Lauf abzubrechen.

import ollama
import json
from datetime import datetime
from pathlib import Path        # oben zu den anderen imports



# --- Hier laden wir den Prompt für das LLM in das Skript rein ---
vorlage = open("prompts/triage_v1.md", encoding = "utf-8").read()

# --- In diesem Abschnitt extrahieren wir wie in compare_labels.py die einzelnen
# Fälle um Sie dem LLM gemeinsam mit dem Prompt zu geben ---
text = open("data/dev.jsonl", encoding = "utf-8").read()
lines = text.splitlines()

prompts = {}

for zeile in lines:
    fall = json.loads(zeile)
    prompt = vorlage.replace("{{NACHRICHT}}", fall["input"])
    prompts[fall["id"]] = prompt # fall["id"] als Schlüssel für das dict, prompt als Wert

# --- Jetzt konfigurieren wir erstmal das LLM und geben es alles was es braucht und
# speichern die Antworten des LLMs einer neu generierten Datei mit Zeitstempel der
# Generierung ---

# Das hier brauchen wir nur um der Datei immer den Namen des aktuellen Testlaufes
# zu geben
stempel = datetime.now().strftime("%Y-%m-%d_%H-%M")
ausgabe = f"runs/{stempel}_qwen2.5-7b_v1.jsonl"
 
 # for x, y in z.item() heißt dass x der Schlüssel ist und y der Wert der von item()
 # extrahiert wird. Die Antworten übertragen wir dann direkt ein eine Datei und zu
 # aller erst erstellen wir natürlich den run Ordner indem die Testläufe dann
 # gespeichert werden. Den Ordner automatisiert erstellen zu lassen hat den Grund,
 # damit das Skript auch von anderen genutzt werden kann, ohne dass ich zuvor
 # erkläre dass ein run Ornder angelegt werden muss.
Path("runs").mkdir(exist_ok=True)
 
with open(ausgabe, "w", encoding = "utf-8") as datei:
        for fall_id, prompt in prompts.items(): 
            antwort = ollama.chat(
            model = "qwen2.5:7b",
            messages = [{"role": "user", "content": prompt}],
            options = {"temperature": 0}
        )
            zeile = json.dumps({"id": fall_id, "antwort": antwort.message.content})
            datei.write(zeile + "\n")
    
        