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
- [x] Schritt 3b: Runner (`scripts/run_eval.py`) — von Vittorio selbst geschrieben.
      Lädt Prompt und Datensatz, ersetzt `{{NACHRICHT}}`, ruft `qwen2.5:7b` über
      Ollama mit Temperature 0 auf, schreibt Rohantworten zeilenweise nach `runs/`.
      Dateiname mit Zeitstempel, Modell und Prompt-Version.
      **Erster Lauf am 16.08.2026: 32/32 Antworten, Parse-Rate 100 %** — alle
      Antworten sauberes einzeiliges JSON ohne Fließtext oder Backticks.
      `dolphin-mistral` liegt für einen späteren Zweitvergleich bereit.
      Offen: `datei.flush()` und Fortschritts-`print` in der Schleife.
      `TODO` für try/except bei Fern-APIs steht im Kopfkommentar.
- [x] Schritt 4: Grader (`scripts/grade.py`) — von Vittorio selbst geschrieben.
      Joint `runs/<lauf>.jsonl` gegen `data/dev.jsonl` über die id, zählt feldweise
      Treffer, gibt Prozente aus und listet jede Abweichung mit id, Soll und Ist.
      Zwei `json.loads` pro Run-Zeile, weil der Runner die Antwort als Text ablegt.
      **Erstes Ergebnis, qwen2.5:7b, triage_v1:** category 87,5 % · priority 62,5 %
      · order_id 100 %. Agreement-Obergrenze: 93,8 / 84,4 / 100 %.
      **Offen:** `order_id` nach Fällen mit und ohne ID trennen (100 % täuscht,
      17 von 32 sind `null`), Confusion-Matrix für `category`, Parse-Rate ausweisen,
      die drei fast gleichen Vergleichsblöcke in eine Funktion ziehen.
- [ ] Schritt 5: Report + Fehleranalyse ← **hier**
- [ ] Schritt 6: Test-Split anlegen
- [ ] Schritt 7: Vergleich mit promptfoo / Inspect

## Befund aus Lauf 1 (17.08.2026) — noch Hypothese

`priority` liegt mit 62,5 % **unter der Majority-Class-Baseline** (immer `normal`
= 65,6 %). Das Feld hat in diesem Zustand negativen Wert. `category` liegt mit
87,5 % nahe der Obergrenze, dort ist kein Handlungsbedarf.

Richtung der 12 Fehler: 10 zu hoch, 2 zu niedrig. Sechs der sieben Hochstufungen
auf `urgent` sind Fälle, die der Prompt **wörtlich als Ausschluss benennt**
(Tonfall 007, Ausfallmeldung 014, Zugangsprobleme 006/022, ausbleibendes Geld 025,
DSGVO 032). Umgekehrt sind 015/016/029 wörtlich Punkte der `low`-Liste und
010/020 wörtlich Schritt 2 — trotzdem falsch.

Vermutung: Das Modell arbeitet den Entscheidungsbaum nicht ab, sondern schätzt nach
Tonfall und gefühlter Schwere. Dazu die bekannte Schwäche verneinter Anweisungen.

Prüfen durch: (a) `triage_v2.md` mit positiven statt verneinten Regeln, gleicher
Datensatz; (b) `dolphin-mistral` mit gleichem Prompt. Bleibt der Bias bei (b),
liegt es nicht am Prompt.

**Achtung Überanpassung:** nicht den Prompt gegen diese 32 Fälle drehen, bis die
Zahl stimmt. Dafür ist der Test-Split da (Schritt 6).

## Lauf 2 (18.08.2026) — dolphin-mistral, Parse-Rate 0/32

Gedacht als Gegenprobe zum `priority`-Bias: gleicher Prompt (`triage_v1`), gleicher
Datensatz, anderes Modell. Nicht auswertbar — aus einem lehrreichen Grund.

`dolphin-mistral:latest` liefert in **32 von 32 Fällen Python-Code statt einer
Klassifikation**: eine Funktion `classify_support_ticket(message)` mit `if/elif`-Ketten
über meine Kategorien, eingerahmt in Backticks. Parsbares JSON: 0.

Zwei Zahlen, die den Befund schärfen:

- Antwortlänge 1.593 Zeichen im Schnitt gegen 66 bei qwen — das 24-fache. Daher die
  Laufzeit von rund 30 Minuten für 32 Fälle; Generierungszeit hängt an der Tokenmenge.
- Nur 23 verschiedene Antworten bei 32 verschiedenen Nachrichten, eine kam viermal
  identisch vor. Bei Temperature 0 ist Wiederholung nur bei gleicher Eingabe erwartbar.
  Heißt: Die Kundennachricht beeinflusst die Ausgabe nicht. Das Modell beantwortet den
  Prompt, nicht den Fall.

**Deutung: kein Prompt-Defekt.** `triage_v1` verbietet Backticks, Fließtext und
Erklärungen wörtlich und zeigt ein Beispiel einer gültigen Antwort. Wer das ignoriert,
kann Instruction Following nicht gut genug — das ist Fähigkeit, nicht Spezifikation.
Vermutung zur Ursache: Der Prompt sieht mit Tabellen, Enum-Werten und nummeriertem
Entscheidungsbaum aus wie ein Anforderungsdokument. Ein schwaches Modell setzt darauf
mit einer Implementierung fort statt mit einer Anwendung.

Konsequenzen:

- `dolphin-mistral` ist als Kandidat ausgeschlossen. Auch das ist ein Eval-Ergebnis —
  Kandidaten auszuschließen ist ein Zweck von Evals, nicht ein Fehlschlag.
- **Die Gegenprobe zum `priority`-Bias bleibt offen.** Ob der Aufwärtsbias am Prompt
  oder am Modell liegt, ist ungeklärt.
- **Parse-Rate ist keine Nebenmetrik.** Ein Report, der nur Accuracy zeigt, hätte hier
  gar nichts angezeigt. `grade.py` bricht an der ersten Zeile ab, weil das `json.loads`
  in Zeile 33 ungeschützt ist — der Fehlerpfad, der bei qwen nie lief.

Rohdaten: `runs/2026-08-18_18-28_dolphin-mistral_v1.jsonl`, nicht versioniert
(`runs/` steht in `.gitignore`).

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
