# Eval_Harness

Ein Eval-Harness für LLM-Systeme, from scratch gebaut. Lernprojekt: das Ziel ist die
Mechanik zu verstehen, nicht ein Framework zu bedienen.

**System under Test:** ein Prompt, der Kundensupport-Nachrichten eines fiktiven
Outdoor-Webshops in strukturiertes JSON überführt — `category` (5 Klassen),
`priority` (3 Klassen), `order_id` (Extraktion mit Normalisierung). Drei Feldtypen,
weil jeder einen anderen Grader und andere Metriken braucht.

## Aufbau

```
spec/task_spec.md      Aufgabendefinition und Labeling-Regeln. Quelle der Wahrheit.
data/dev.jsonl         Datensatz: 32 Fälle, Input + erwarteter Output + Metadaten
data/blind.jsonl       Unabhängige Zweitlabels, eingefroren. Basis des Agreement-Werts
data/dev_v1.0_snapshot.jsonl   Labelstand vor der Adjudikation
scripts/               Validator, Vergleichsskript, später Runner und Grader
```

## Setup

Python 3.10 oder neuer. Alles Weitere im Projektordner:

```bash
python3 -m venv .venv          # virtuelle Umgebung anlegen (einmalig)
source .venv/bin/activate      # aktivieren (in jeder neuen Terminal-Sitzung)
pip install -r requirements.txt
```

Eine **virtuelle Umgebung** ist Pythons Antwort auf ein Problem, das Java über Maven
löst: `pip install` schreibt sonst systemweit, und zwei Projekte mit unterschiedlichen
Versionsanforderungen zerstören sich gegenseitig. `.venv/` ist ein projektlokaler
Python samt eigener Paketablage und steht in `.gitignore` — man committet die Umgebung
nicht, sondern `requirements.txt`, aus der sie sich rekonstruieren lässt.

Aktiv erkennt man sie am `(.venv)` vor dem Prompt. `deactivate` beendet sie.

## Ausführen

```bash
python3 scripts/validate_dataset.py data/dev.jsonl
python3 scripts/compare_labels.py data/dev_v1.0_snapshot.jsonl data/blind.jsonl
```

Der Validator prüft Schema, erlaubte Labelwerte, ID-Format und Duplikate und gibt die
Klassenverteilung aus. Vor jeder Änderung am Datensatz laufen lassen.

## Arbeitsregeln

Diese Regeln sind aus Fehlern entstanden, nicht aus Prinzipien:

**Erst Spec, dann Daten.** Ein Label ohne schriftliche Regel ist nicht reproduzierbar.

**Jede Regel muss allein aus dem Input entscheidbar sein.** Eine Regel, die Wissen über
die Welt verlangt ("betrifft alle Nutzer"), erzeugt Uneinigkeit, die wie Unaufmerksamkeit
aussieht, aber ein Spec-Fehler ist.

**Bei Uneinigkeit erst die Spec ändern, dann das Label.** Nie umgekehrt. Jede
Regeländerung wird in der Änderungshistorie der Spec mit ihrem Auslöser festgehalten.

**Blindlabels bleiben eingefroren.** `data/blind.jsonl` wird nach der Adjudikation nicht
korrigiert — sonst misst der Agreement-Wert nur noch, wie oft man sich hinterher geeinigt
hat. Deshalb existiert `dev_v1.0_snapshot.jsonl`: der Vergleich läuft gegen den Stand vor
der Diskussion.

**Vor jeder Label-Änderung committen.** Der Datensatz ist Code.

**Schwere Fälle gehören rein.** Ein Datensatz aus einfachen Fällen misst nichts. 41 % der
Fälle sind als `hard` markiert; eine Baseline bei 95 % wäre ein Warnsignal, kein Erfolg.

## Stand

- [x] Aufgabe und Erfolgskriterium (`spec/task_spec.md`, Version 1.1)
- [x] Dev-Datensatz, 32 Fälle, mit Schema-Validator
- [x] Blind-Review: 32 unabhängige Zweitlabels, 7 Abweichungen, daraus 3 Spec-Defekte
      behoben und 4 Labels adjudiziert
- [ ] `scripts/compare_labels.py` (Aufgabe: `scripts/AUFGABE_compare_labels.md`)
- [ ] Runner — führt das SUT über alle Fälle aus, cached Ergebnisse
- [ ] Grader — feldweiser Vergleich Ist gegen Soll
- [ ] Report — aggregierte Metriken und Fehleranalyse
- [ ] Test-Split, sobald die Spec stabil ist
- [ ] Vergleich mit promptfoo / Inspect
