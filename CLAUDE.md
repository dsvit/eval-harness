# Eval_Harness — Arbeitskontext

**Inhaltliches steht im `README.md`**: Zweck, System under Test, die vier Bausteine,
getroffene Entscheidungen mit Begründung, Kernprinzipien, bisherige Ergebnisse.
Diese Datei enthält nur, was beim Arbeiten zählt und im README nichts zu suchen hat.

Verbindliche Aufgabendefinition: `spec/task_spec.md`, aktuell Version 1.1.
Repo: github.com/dsvit/eval-harness

## Stand

- [x] Schritt 0: Aufgabe und Erfolgskriterium (`spec/task_spec.md`)
- [x] Schritt 1: Dev-Datensatz, 32 Fälle, plus Schema-Validator
- [x] Schritt 2: Blind-Review (`data/blind.jsonl`, eingefroren)
      7 Abweichungen, davon 6 auf 3 Spec-Defekte zurückführbar. `order_id` 32/32.
      Spec auf 1.1 gehoben, danach 4 Labels adjudiziert.
      Vorzustand: `data/dev_v1.0_snapshot.jsonl`
- [x] Schritt 2b: `scripts/compare_labels.py` — von Vittorio selbst geschrieben.
      Zählt Übereinstimmung bei allen drei Feldern: 30/32, 27/32, 32/32.
      **Offen:** Prozentangaben, Liste der strittigen Fälle, optional Cohens Kappa.
      Danach: die drei fast gleichen Blöcke in eine Funktion ziehen — die Dopplung
      steht bewusst noch drin, damit der Bedarf spürbar wird.
- [x] Schritt 3a: `prompts/triage_v1.md` — von Vittorio aus der Spec abgeleitet,
      von Claude auf Kontamination geprüft. Befund: Beispiel-IDs in der Spec stammten
      aus Testfällen, wurden im Prompt durch neutrale ersetzt.
- [~] Schritt 3b: Runner (`scripts/run_eval.py`) ← **hier**
      **Stand:** Verbindung zu Ollama steht, fest verdrahteter Testaufruf funktioniert.
      **Offen:** Prompt laden, Platzhalter `{{NACHRICHT}}` ersetzen, Schleife über
      `data/dev.jsonl`, Antworten nach `runs/` schreiben, Parse-Fehler abfangen
      statt abstürzen.
      Modell: `qwen2.5:7b` über Ollama, lokal. `dolphin-mistral` liegt für einen
      späteren Zweitvergleich bereit. Temperature 0 setzen.
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
  ist ein anderes Problem als eine unwahre Sachbehauptung. In konkrete Testfälle
  übersetzen, nicht nur konzeptionell beantworten — Kandidat für einen adversarialen Split.

- **Abschlussdokument.** Vittorio wünscht sich am Ende eine ausführliche Einordnung:
  was wurde gebaut, warum in dieser Reihenfolge, was hat welcher Schritt gebracht.
  Fällig, wenn Report und Test-Split stehen.

## Arbeitsweise

Vittorio schreibt Deutsch, ist Anfänger im Eval-Bereich und will **verstehen**, nicht nur
Ergebnisse. Konzepte erklären, Gegenwind geben wenn die Vorgehensweise nicht optimal ist.
Antworten knapp halten.

**Kein Code ohne Durchgang.** Vittorio (16.08.2026): Code, den er weder geschrieben noch
Zeile für Zeile durchgegangen ist, bleibt ein Fremdkörper im eigenen Projekt — Verständnis
hängt an Autorschaft. Entstanden an `scripts/validate_dataset.py`, das Claude am ersten Tag
ungefragt mitgeliefert hat.

Konsequenz: Vor dem Schreiben von Code fragen, ob er gebraucht wird und wer ihn schreibt.
Schreibt Claude, danach gemeinsam durchgehen — Zeile für Zeile, inklusive *wozu* das
Konstrukt gut ist und *warum* man so etwas überhaupt braucht. Nicht nur erklären, was der
Code tut.

**Nicht in zu kleine Stufen zerlegen.** Vittorio (16.08.2026): Wenn er einen Ablauf schon
verstanden hat, bremst die Zerlegung in Mikroschritte mehr als sie hilft. Stufen nur dort,
wo tatsächlich neue Konzepte auftauchen.

**Offen:** `scripts/validate_dataset.py` gemeinsam durchgehen. Alternativ von Vittorio
neu schreiben lassen oder löschen — seine Entscheidung.
