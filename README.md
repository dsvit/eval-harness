# Eval_Harness

Ein Eval-Harness für LLM-Systeme, from scratch gebaut. Lernprojekt: das Ziel ist, die
Mechanik zu verstehen, nicht ein Framework zu bedienen.

## System under Test

Ein Prompt, der eingehende Kundensupport-Nachrichten eines fiktiven Outdoor-Webshops
("Nordlicht") in strukturiertes JSON überführt:

| Feld | Typ | Aufgabentyp |
|---|---|---|
| `category` | Enum, 5 Werte | Mehrklassen-Klassifikation |
| `priority` | Enum, 3 Werte | Ordinale Klassifikation |
| `order_id` | String oder `null` | Extraktion mit Normalisierung |

Bewusst so gewählt: Die drei Feldtypen brauchen unterschiedliche Grader und unterschiedliche
Metriken. Die verbindliche Aufgabendefinition steht in `spec/task_spec.md` — das ist die
Quelle der Wahrheit für alle Labels.

## Die vier Bausteine

```
Dataset  →  Runner  →  Grader  →  Report
```

**Dataset** — Eingaben, erwartete Ausgaben, Metadaten.
**Runner** — schickt jeden Fall durch das SUT, speichert die Rohantworten.
**Grader** — vergleicht Ist gegen Soll, feldweise.
**Report** — aggregierte Metriken und Fehleranalyse.

Die Reihenfolge ist nicht beliebig: Jeder Schritt lässt sich erst bauen, wenn man dem
vorherigen trauen kann.

## Aufbau

```
spec/task_spec.md              Aufgabendefinition und Labeling-Regeln, versioniert
prompts/triage_v1.md           der Prompt = das System under Test
data/dev.jsonl                 32 Fälle: Input + erwarteter Output + Metadaten
data/blind.jsonl               unabhängige Zweitlabels, eingefroren
data/dev_v1.0_snapshot.jsonl   Labelstand vor der Adjudikation
scripts/                       Validator, Vergleichsskript, Runner
runs/                          Rohantworten der Modellläufe (nicht versioniert)
```

## Bisherige Ergebnisse

**Inter-Annotator Agreement.** Bevor irgendein Modell gemessen wurde, haben zwei Menschen
denselben Datensatz unabhängig gelabelt. Das Ergebnis ist die Obergrenze jeder späteren
Messung:

| Feld | Übereinstimmung | |
|---|---|---|
| `order_id` | 32 / 32 | Extraktionsregeln eindeutig |
| `category` | 30 / 32 | gut |
| `priority` | 27 / 32 | Schwachstelle |

Praktische Folge: Ein Modellergebnis von 84 % bei `priority` wäre nicht interpretierbar —
dort sind sich nicht einmal zwei Menschen einig. Bei `order_id` ist jede Abweichung ein
echter Modellfehler.

**Drei Spec-Defekte, gefunden durch das Zweitlabeling.** Sechs der sieben Abweichungen
gingen auf Regelfehler zurück, nicht auf Unaufmerksamkeit:

- Ein `urgent`-Kriterium verlangte Wissen, das aus der Nachricht nicht hervorging
  ("betrifft alle Nutzer"). Ein Labeler hat nur den Text — solche Regeln erzeugen Rateverhalten.
- Zwei Regeln standen korrekt in der Spec, wurden beim Labeln aber nicht gefunden. Eine Regel,
  die niemand findet, ist so kaputt wie eine fehlende. Daraufhin wurde `priority` von Fließtext
  auf einen Entscheidungsbaum umgestellt.
- Die `low`-Definition hing an einem unscharfen Begriff und wurde durch eine abschließende
  Liste ersetzt.

Die vollständige Änderungshistorie mit Auslöser pro Regel steht am Ende von
`spec/task_spec.md`.

## Getroffene Entscheidungen

| Entscheidung | Begründung |
|---|---|
| Python statt Java | Das LLM-Ökosystem ist Python; für Java gibt es keine Eval-Tooling-Landschaft |
| From scratch statt promptfoo/Inspect | Lernziel ist die Mechanik. Frameworks später zum Vergleich |
| JSONL statt CSV/JSON | Zeilenweise appendbar, git-diffbar, Standard im Eval-Umfeld |
| Lokales Modell über Ollama | Kostenlos, unbegrenzt wiederholbar. Ein schwaches Modell erzeugt echte Fehler zum Analysieren |
| Labels vorgeschlagen, nicht diktiert | Jedes Label wurde blind gegengelabelt. Uneinigkeit = Spec-Bug, nicht Label-Bug |
| Blindlabels eingefroren | Nachträgliche Korrektur würde den Agreement-Wert wertlos machen |
| Nur `dev`-Split zu Beginn | Ein Test-Split entsteht erst, wenn die Spec stabil ist — sonst ist er kontaminiert |

## Kernprinzipien

Entstanden aus Fehlern, nicht aus Lehrbüchern:

**Erst Spec, dann Daten.** Ein Label ohne schriftliche Regel ist nicht reproduzierbar.
Labeln zwei Menschen unterschiedlich, ist die Spec unterspezifiziert — nicht der Mensch schuld.

**Jede Regel muss allein aus dem Input entscheidbar sein.** Regeln, die Wissen über die Welt
verlangen, erzeugen Uneinigkeit, die wie Unaufmerksamkeit aussieht.

**Bei Uneinigkeit erst die Spec ändern, dann das Label.** Nie umgekehrt. Jede Regeländerung
wird mit ihrem Auslöser dokumentiert.

**Ton ist keine Priorität.** Eine wütende Formulierung erhöht die Dringlichkeit nicht.

**Schwere Fälle gehören rein.** 41 % der Fälle sind als `hard` markiert. Eine Baseline bei
95 % wäre ein Warnsignal, kein Erfolg.

**Vor jeder Label-Änderung committen.** Der Datensatz ist Code.

## Setup

Python 3.10 oder neuer, dazu [Ollama](https://ollama.com) mit einem lokalen Modell.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:7b
```

## Ausführen

```bash
python3 scripts/validate_dataset.py data/dev.jsonl
python3 scripts/compare_labels.py
```

Der Validator prüft Schema, erlaubte Labelwerte, ID-Format und Duplikate und gibt die
Klassenverteilung aus. Vor jeder Änderung am Datensatz laufen lassen.

## Stand

- [x] Aufgabendefinition und Labeling-Regeln (`spec/task_spec.md`, Version 1.1)
- [x] Dev-Datensatz, 32 Fälle, mit Schema-Validator
- [x] Blind-Review, Agreement gemessen, 3 Spec-Defekte behoben
- [x] Prompt v1 (`prompts/triage_v1.md`)
- [~] Runner — Verbindung zum Modell steht, Schleife über den Datensatz fehlt
- [ ] Grader — feldweiser Vergleich Modell gegen Gold
- [ ] Report — Metriken und Fehleranalyse
- [ ] Test-Split
- [ ] Vergleich mit promptfoo / Inspect
