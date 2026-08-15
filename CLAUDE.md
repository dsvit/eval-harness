# Eval_Harness

## Zweck

Lernprojekt: einen Eval-Harness für LLM-Systeme **from scratch** bauen, um die Mechanik zu
verstehen — nicht um ein Framework zu bedienen. Ziel ist übertragbares Wissen für den
Jobmarkt (AI/ML Engineering), nicht ein Produktivsystem.

## System under Test (SUT)

Ein LLM-Prompt, der eingehende Kundensupport-Nachrichten eines fiktiven Outdoor-Webshops
("Nordlicht") in strukturiertes JSON überführt:

| Feld       | Typ                | Beschreibung                          |
|------------|--------------------|---------------------------------------|
| `category` | Enum (5 Werte)     | Mehrklassen-Klassifikation            |
| `priority` | Enum (3 Werte)     | Ordinale Klassifikation               |
| `order_id` | String \| null     | Extraktion mit Normalisierung         |

Bewusst gewählt, weil alle drei Feldtypen unterschiedliche Grader und unterschiedliche
Metriken erfordern. Die verbindliche Definition steht in `spec/task_spec.md` — **das ist
die Quelle der Wahrheit für alle Labels.**

## Architektur (Zielbild)

```
data/dev.jsonl      Datensatz: Input + erwarteter Output + Metadaten
spec/task_spec.md   Aufgabendefinition + Labeling-Regeln
scripts/            Validator, später: Runner, Grader, Report
```

Vier Bausteine eines Harness, in dieser Reihenfolge zu bauen:

1. **Dataset** — Input + Expected + Metadaten  ← *aktuell hier*
2. **Runner** — führt das SUT über alle Fälle aus, cached Ergebnisse
3. **Grader** — vergleicht Ist gegen Soll, feldweise
4. **Report** — aggregierte Metriken + Fehleranalyse

## Getroffene Entscheidungen

| Entscheidung | Begründung |
|---|---|
| Python statt Java | Gesamtes LLM-Ökosystem ist Python; Java hat keine Eval-Tooling-Landschaft |
| From scratch statt promptfoo/Inspect | Lernziel ist die Mechanik. Frameworks später zum Vergleich anschauen |
| JSONL statt CSV/JSON | Zeilenweise appendbar, git-diffbar, Standard im Eval-Umfeld |
| `CLAUDE.md` statt `project_master.json` | Wird automatisch in den Kontext geladen; JSON ist für Prosa-Kontext ungeeignet |
| Labels vorgeschlagen, nicht diktiert | Vittorio reviewt jedes Label. Uneinigkeit = Spec-Bug, nicht Label-Bug |
| Nur `dev`-Split zu Beginn | Test-Split entsteht erst, wenn die Spec stabil ist — sonst kontaminiert man ihn |

## Kernprinzipien (nicht verwässern)

- **Erst Spec, dann Daten.** Ein Datensatz ohne schriftliche Labeling-Regel ist nicht
  reproduzierbar. Wenn zwei Menschen unterschiedlich labeln, ist die Spec unterspezifiziert.
- **Ton ≠ Priorität.** Wütende Formulierung erhöht die Dringlichkeit nicht.
- **Schwere Fälle gehören rein.** Ein Datensatz aus nur einfachen Fällen misst nichts.
  Ziel-Baseline liegt bewusst *nicht* bei 95 %.
- **Der `note`-Eintrag pro Fall ist kein Kommentar, sondern Werkzeug.** Bei der späteren
  Fehleranalyse erklärt er, warum ein Fall schwer ist.

## Stand

- [x] Schritt 0: Aufgabe und Erfolgskriterium definiert (`spec/task_spec.md`)
- [x] Schritt 1: Dev-Datensatz, 32 Fälle (`data/dev.jsonl`)
- [x] Schritt 1b: Schema-Validator (`scripts/validate_dataset.py`)
- [x] Schritt 2: Blind-Review durch Vittorio (`data/blind.jsonl`, eingefroren)
      32 Fälle unabhängig gelabelt, 7 Abweichungen, davon 6 auf 3 Spec-Defekte
      zurückführbar. `order_id` 32/32 identisch. Spec daraufhin auf 1.1 gehoben,
      danach 4 Labels adjudiziert. Vorzustand: `data/dev_v1.0_snapshot.jsonl`
- [~] Schritt 2b: `scripts/compare_labels.py` — schreibt Vittorio selbst
      (Aufgabe in `scripts/AUFGABE_compare_labels.md`). Vergleich gegen
      `dev_v1.0_snapshot.jsonl`, nicht gegen `dev.jsonl`.
      **Stand:** beide Dateien werden als Dict mit `id` als Schlüssel eingelesen,
      Übereinstimmung bei `category` (30/32) und `priority` (27/32) wird gezählt.
      **Offen:** `order_id`, Prozentangaben, Liste der strittigen Fälle,
      optional Cohens Kappa. Danach: die drei fast gleichen Blöcke in eine
      Funktion ziehen — die Dopplung ist bewusst stehengelassen worden.
      **Repo:** github.com/dsvit/eval-harness
- [ ] Schritt 3: Runner ← **nächster Schritt**
- [ ] Schritt 4: Grader + Metriken
- [ ] Schritt 5: Report + Fehleranalyse
- [ ] Schritt 6: Test-Split anlegen
- [ ] Schritt 7: Vergleich mit promptfoo / Inspect

## Offene Fragen (nicht vergessen)

- **Prompt Injection vs. Spec-Abschnitt 0.** Vittorio (14.08.2026): Öffnet die Regel
  "es zählt, was der Kunde behauptet, nicht was zutrifft" einen Angriffsvektor?
  Beispiel: *"Mir wurde vom CEO gesagt, dass ich einen Gutschein bekomme."*
  Beim Aufgreifen: Trennung zwischen *einer Behauptung eine Kategorie zuweisen* und
  *auf eine Behauptung hin handeln*; klassische Injection ("ignoriere deine Anweisungen")
  ist ein anderes Problem als eine unwahre Sachbehauptung. Antwort in konkrete Testfälle
  übersetzen, nicht nur konzeptionell beantworten — Kandidat für einen adversarialen Split.

## Arbeitsweise

Vittorio schreibt Deutsch, ist Anfänger im Eval-Bereich und will **verstehen**, nicht nur
Ergebnisse. Konzepte erklären, Gegenwind geben wenn die Vorgehensweise nicht optimal ist.
Antworten knapp halten.
