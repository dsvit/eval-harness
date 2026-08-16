import ollama

# Runner für den Eval-Harness.
#
# Ziel: liest die Kundennachrichten aus data/dev.jsonl, setzt jede in den Prompt
# aus prompts/triage_v1.md ein, schickt sie ans Modell und speichert die Antworten
# nach runs/. Nur der input geht ans Modell -- expected bleibt zurück und wird
# erst später vom Grader zum Abgleich benutzt.
#
# Aktueller Stand: fest verdrahteter Testaufruf, prüft nur die Verbindung.
antwort = ollama.chat(
    model="qwen2.5:7b",
    messages=[{"role": "user", "content": "Antworte nur mit dem Wort: Hallo"}],
)

print(antwort.message.content)