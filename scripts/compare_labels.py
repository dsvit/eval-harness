import json

# --- Datei blind.jsonl einlesen ---

# Durch open öffnen wir den Datei-Inhalt. Mit .read() lesen wir den gesamten Inhalt von blind.jsonl und geben ihn zurück.

text = open("data/blind.jsonl", encoding = "utf-8").read()

# Zerlegt den Text an den Umbrüchen
lines = text.splitlines()


# --- Eine Zeile in ein Dict umwandeln ---

vittorio = {} # Das bildet das Dict ab in dem die einzelnen Fälle gespeichert werden.

# Jede Zeile in ein Dict umwandeln und unter ihrer id ablegen,damit beide Dateien später über die id verglichen werden können.
for zeile in lines:
    fall = json.loads(zeile)
    vittorio[fall["id"]] = fall


# --- Das ganze haben wir nun mit blind.jsonl gemacht und nun tun wir das mit dev_v1.0_snapshot.jsonl -> Also der Datei die Claude bewertet hat um zu schauen, dass die Bewertung zuverlässig klappt. Ein wesentlicher Unterschied: Das Labelfeld heißt in dieser Datei nicht "label" wie bei der blind-Datei sondern "exptected" ---

text = open("data/dev_v1.0_snapshot.jsonl", encoding = "utf-8").read()
lines = text.splitlines()

claude = {}

for zeile in lines:
    fall = json.loads(zeile)
    claude[fall["id"]] = fall
    
# Jetzt können wir vergleichen ob die Anzahl an Zeilen stimmt & in wie vielen Labels wir das gleiche getippt haben

# Raus kommen müsste 32 32, dann sind die Fälle vollständig eingelesen beiderseits
print(f"Anzahl an Fällen in (vittorio, claude): ({len(vittorio)}, {len(claude)})") 

# Dieser zählt wie oft meine labels & priorities mit denen von Claude gleich sind
treffer_labels = 0
treffer_priority = 0
treffer_order_id = 0

# Vergleicht die labels & priorites
for fall_id in vittorio:
  
    if(vittorio[fall_id]["label"]["category"] == claude[fall_id]["expected"]["category"]):
        treffer_labels +=1
    
    if(vittorio[fall_id]["label"]["priority"] == claude[fall_id]["expected"]["priority"]):
        treffer_priority +=1
        
    if(vittorio[fall_id]["label"]["order_id"] == claude[fall_id]["expected"]["order_id"]):
          treffer_order_id +=1
        
# Ausgabe des Ergebnis
print(f"Treffer der labels: {treffer_labels}")
print(f"Treffer der priorities: {treffer_priority}")
print(f"Treffer der order_id's: {treffer_order_id}")
