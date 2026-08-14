# Aufgabe: `scripts/compare_labels.py` selbst schreiben

Du baust das Skript, das deine Blind-Labels gegen meine Vorschläge vergleicht.
`scripts/validate_dataset.py` bleibt als gelöstes Beispiel liegen — schau dort rein,
wenn du wissen willst, wie man in Python eine JSONL-Datei liest oder Argumente entgegennimmt.

---

## Was rein geht

Zwei Dateien, beide JSONL (ein JSON-Objekt pro Zeile):

```
data/dev_v1.0_snapshot.jsonl   → Labels stehen unter dem Schlüssel  "expected"
data/blind.jsonl               → Labels stehen unter dem Schlüssel  "label"
```

**Nicht** gegen `data/dev.jsonl` vergleichen. Dort stehen inzwischen die adjudizierten
Labels, also solche, die aus der gemeinsamen Diskussion entstanden sind. Der Agreement-Wert
muss gegen den Stand *vor* der Diskussion gerechnet werden, sonst misst er nur noch, wie
oft ihr euch hinterher geeinigt habt.

Beide haben dasselbe `id`-Feld (`dev-001` … `dev-032`). Über die `id` verbindest du sie.
Beide Labelobjekte haben dieselben drei Felder: `category`, `priority`, `order_id`.

Noch nicht gelabelte Einträge in `blind.jsonl` enthalten `"?"`. Die müssen raus,
bevor du rechnest — sonst zählst du "nicht bearbeitet" als "uneinig".

## Was raus kommt

Auf die Konsole, keine Datei:

1. Wie viele Fälle überhaupt schon gelabelt sind
2. Pro Feld: wie oft ihr euch einig seid, absolut und in Prozent
3. Wie viele Fälle in **allen drei** Feldern übereinstimmen
4. Eine Liste der strittigen Fälle: `id`, der Nachrichtentext, und pro abweichendem
   Feld beide Werte nebeneinander

Punkt 4 ist der eigentliche Zweck. Die Prozentzahlen sind nur Beiwerk — die Konfliktliste
ist das, womit wir danach die Spec reparieren.

---

## In Stufen bauen

Nicht alles auf einmal. Nach jeder Stufe laufen lassen.

**Stufe 0** — Datei öffnen, Zeilen zählen, Zahl ausgeben.

**Stufe 1** — Beide Dateien in je ein Dict laden: `{"dev-001": {...}, ...}`.
Eine Zeile aus jedem Dict ausgeben, um zu sehen ob die Struktur stimmt.

**Stufe 2** — Unfertige Fälle (`"?"`) aussortieren. Ausgeben, wie viele übrig sind.

**Stufe 3** — Pro Feld zählen, wie oft beide Werte gleich sind. Prozent ausrechnen.

**Stufe 4** — Konfliktliste ausgeben.

**Stufe 5 (optional, Mathe)** — Cohens Kappa.
Das Problem, das es löst: 66 % unserer `priority`-Labels sind `normal`. Zwei Leute,
die stumpf immer `normal` raten, sind sich zu 66 % "einig" — die Zahl sagt also nichts.
Kappa zieht die zufällig zu erwartende Übereinstimmung heraus:

```
po = Anteil der Fälle, in denen ihr tatsächlich übereinstimmt
pe = Summe über alle Klassen c von:  (Anteil c bei A) * (Anteil c bei B)
kappa = (po - pe) / (1 - pe)
```

Faustregel: unter 0,4 schwach · 0,4–0,6 mäßig · 0,6–0,8 gut · über 0,8 sehr gut.

---

## Java → Python Spickzettel

Du kannst programmieren, dir fehlt die Syntax. Nur das, was du hier brauchst:

| Java | Python |
|---|---|
| `{ ... }` Blöcke | Einrückung (4 Leerzeichen). Der Doppelpunkt eröffnet den Block. |
| `;` am Zeilenende | gibt es nicht |
| `String s = "x";` | `s = "x"` — keine Typdeklaration nötig |
| `HashMap<String, Foo>` | `dict` → `d = {}`, `d["key"] = wert`, `d.get("key")` |
| `ArrayList<String>` | `list` → `xs = []`, `xs.append("a")` |
| `for (String x : xs)` | `for x in xs:` |
| `map.entrySet()` | `for key, value in d.items():` |
| `xs.size()` / `map.size()` | `len(xs)` |
| `String.format("%d von %d", a, b)` | `f"{a} von {b}"` — f-String, Ausdruck direkt in den Klammern |
| `System.out.println(x)` | `print(x)` |
| `public static void main` | `if __name__ == "__main__":` ganz unten |
| `args[0]` | `sys.argv[1]` (`sys.argv[0]` ist der Skriptname) |
| `x == null` | `x is None` |
| ternär `a ? b : c` | `b if a else c` |

Was du in Java so nicht hast und hier brauchst:

```python
import json
obj = json.loads(zeile)            # String  → dict
text = open(pfad, encoding="utf-8").read()
for zeile in text.splitlines():
    if zeile.strip():              # Leerzeilen überspringen
        ...
```

**List Comprehension** — die eine Python-Eigenheit, die sich lohnt. Statt einer Schleife,
die in eine Liste anhängt, schreibt man:

```python
ids = [r["id"] for r in rows]                       # alle ids
offen = [r for r in rows if r["label"]["category"] == "?"]   # gefiltert
treffer = sum(1 for r in rows if bedingung(r))      # zählen ohne Zwischenliste
```

Formatierte Ausgabe: `f"{wert:>6.0%}"` macht aus `0.8125` → `   81%`.
Das `>` heißt rechtsbündig, `6` die Breite, `.0%` Prozent ohne Nachkommastellen.

---

## Testen

Ausführen:

```
python3 scripts/compare_labels.py data/dev_v1.0_snapshot.jsonl data/blind.jsonl
```

Zum Prüfen deiner Zählung kannst du eine Datei gegen sich selbst laufen lassen —
`data/dev_v1.0_snapshot.jsonl` zweimal muss überall 100 % ergeben. Dafür musst du kurz
den Schlüssel anpassen, weil dort `expected` statt `label` steht. Wenn 100 % rauskommt,
zählst du richtig.

Zeig mir deinen Code, wenn du durch bist oder festhängst. Ich sage dir, was unpythonisch
ist, aber schreibe ihn nicht für dich um.
