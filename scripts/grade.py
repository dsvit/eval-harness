import json

# --- Einlesen der Dateien die wir vergleichen wollen ---

# Erst einmal unsere SOT
text_dev = open("data/dev.jsonl", encoding = "utf-8").read()

lines_dev = text_dev.splitlines()

# Jetzt der Modell Output
text_modell = open("runs/2026-08-16_22-10_qwen2.5-7b_v1.jsonl", encoding = "utf-8").read()

lines_modell = text_modell.splitlines()

# --- Nun fügen wir die einzelnen Zeilen in dicts ein die wir
# dann vergleichen können ---

gold = {} # aus text_dev

modell = {} # aus modell_run

nicht_parsbar = [] # Liste mit den ID's der Einträge die nicht parsbar waren

for zeile in lines_dev:
    fall = json.loads(zeile)
    gold[fall["id"]] = fall
    
# Zwei json.loads statt einem: Der Runner speichert die Modellantwort als
# reinen Text. Der erste Aufruf macht aus der Zeile ein Dict mit "id" und
# "antwort", der zweite macht aus dem Text in "antwort" wieder ein Dict.
# Erst dann kommt man an "category" usw. heran.
# Die id steht nur aussen in eintrag -- das Modell liefert keine mit.
for zeile in lines_modell:
    eintrag = json.loads(zeile)
    try:
        fall = json.loads(eintrag["antwort"])
        modell[eintrag["id"]] = fall
    except json.JSONDecodeError:
        nicht_parsbar.append(eintrag["id"])
    
# --- Jetzt graden wir den Output des LLM's ---
treffer_labels = 0
treffer_priority = 0
treffer_order_id = 0

for fall_id in gold:
    if fall_id not in modell:
        continue
    
    if(modell[fall_id]["category"] == gold[fall_id]["expected"]["category"]):
        treffer_labels +=1
    else:
        print(f'ID: {fall_id} | modell-category: {modell[fall_id]["category"]} vs gold-category: {gold[fall_id]["expected"]["category"]}')
        
    if(modell[fall_id]["priority"] == gold[fall_id]["expected"]["priority"]):
        treffer_priority +=1
    else:
        print(f'ID: {fall_id} | modell-priority: {modell[fall_id]["priority"]} vs gold-priority: {gold[fall_id]["expected"]["priority"]}')
            
    if(modell[fall_id]["order_id"] == gold[fall_id]["expected"]["order_id"]):
        treffer_order_id +=1
    else:
        print(f'ID: {fall_id} | modell-order_id: {modell[fall_id]["order_id"]} vs gold-order_id: {gold[fall_id]["expected"]["order_id"]}')
              
# Ausgabe des Ergebnis
gesamt = len(gold)
geparsed = len(modell)

print("========== PARSE-RATE ==========")
print(f"Parse-Rate: {geparsed}/{gesamt} = {geparsed / gesamt * 100:.1f}%")

print(f"nicht parsbar: {nicht_parsbar}")

print("========== GESAMT-ACCURACY ==========")
print(f"category:  {treffer_labels}/{gesamt}  =  {treffer_labels / gesamt * 100:.1f} %")
print(f"priority:  {treffer_priority}/{gesamt}  =  {treffer_priority / gesamt * 100:.1f} %")
print(f"order_id:  {treffer_order_id}/{gesamt}  =  {treffer_order_id / gesamt * 100:.1f} %")

# Wenn die Parse-Rate = 0% ist können wir die if-Verzweigung nicht ausführen, da man nicht durch 0 teilen kann
if geparsed != 0:
    print("========== CONDITIONAL-ACCURACY ==========")
    print(f"category:  {treffer_labels}/{geparsed}  =  {treffer_labels / geparsed * 100:.1f} %")
    print(f"priority:  {treffer_priority}/{geparsed}  =  {treffer_priority / geparsed * 100:.1f} %")
    print(f"order_id:  {treffer_order_id}/{geparsed}  =  {treffer_order_id / geparsed * 100:.1f} %")
else:
    print("Conditional-Accuracy kann nicht berechnet werden, da Parse-Rate = 0% und man nicht treffer/0 rechnen kann.")
    