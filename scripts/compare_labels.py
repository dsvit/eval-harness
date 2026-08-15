text = open("data/blind.jsonl", encoding="utf-8").read() # Durch open öffnen wir den Datei-Inhalt. Mit .read() lesen wir den gesamten Inhalt von blind.jsonl und geben ihn zurück.

lines = text.splitlines() # Zerlegt den Text an den Umbrüchen

print(len(lines)) # Gibt uns die Anzahl der Zeilen aus. Da eine Zeile einen Fall abbildet, kann man auch sagen, dass uns das die Anzahl an Fälle zurückgibt.