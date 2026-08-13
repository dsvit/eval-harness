# Task Spec — Support-Ticket-Triage

**Version 1.1** · Diese Datei ist die Quelle der Wahrheit für alle Labels in `data/`.
Wenn ein Label und diese Spec sich widersprechen, ist zuerst die Spec zu klären.
Änderungshistorie steht am Ende.

---

## 0. Grundregel

**Jede Regel in dieser Spec muss allein aus dem Nachrichtentext entscheidbar sein.**

Ein Labeler hat nichts außer der Nachricht. Er weiß nicht, ob der Server wirklich
ausgefallen war, ob die Bestellung tatsächlich über 50 € lag oder ob die Erstattung
intern schon angewiesen wurde. Eine Regel, die solches Wissen verlangt, ist unbrauchbar —
zwei Labeler raten dann unterschiedlich, und die Uneinigkeit sieht aus wie Unaufmerksamkeit,
obwohl sie ein Spec-Fehler ist.

Wo es um Tatsachen geht, zählt daher immer, **was der Kunde behauptet**, nicht, was zutrifft.

---

## 1. Aufgabe

Gegeben ist eine eingehende Kundennachricht an den Support des fiktiven Outdoor-Webshops
**Nordlicht**. Das System gibt genau ein JSON-Objekt zurück:

```json
{ "category": "shipping", "priority": "normal", "order_id": "NL-482913" }
```

Keine Erklärung, kein Fließtext, keine zusätzlichen Felder.

---

## 2. `category` — genau ein Wert

**Wozu das Feld dient:** `category` ist ein **Routing-Ziel** — welches Team bekommt das
Ticket auf den Tisch. Es beschreibt *nicht* die technische Ursache. Diese Unterscheidung
entscheidet die meisten Grenzfälle.

| Wert        | Zuständiges Team, umfasst |
|-------------|---------------------------|
| `billing`   | Rechnungen, Zahlungen, Abbuchungen, Preise, Gutscheine, **Erstattungen** |
| `technical` | Website- oder App-Fehler, Bugs, nicht funktionierende Links oder Mails |
| `account`   | Login, Passwort, 2FA, Stammdaten, Kontolöschung, Sicherheitsvorfälle |
| `shipping`  | Lieferung, Tracking, Verlust, Beschädigung, Umtausch, **Retouren-Logistik** |
| `other`     | Produktfragen, Lob, Beschwerden ohne Vorgang, Werbung, Spam |

### Tie-Breaker (in dieser Reihenfolge anwenden)

1. **Blocker schlägt Ziel.** Was den Kunden *aktuell aufhält*, bestimmt die Kategorie —
   nicht, was er ursprünglich vorhatte.
   → *"Ich komme nicht ins Konto und kann meine Rechnung nicht laden"* = `account`.
2. **Geld schlägt Logistik.** Retoure unterwegs oder Rücksendeschein = `shipping`.
   Sobald es um die **Erstattung** geht = `billing`.
3. **Zugang schlägt Technik.** Ein technischer Fehler, der den Kontozugang betrifft,
   ist `account` — auch wenn der Bug woanders sitzt.
   → *Reset-Mail kommt nicht an* = `account`, obwohl der Mailversand defekt ist.
   → *2FA-Code wird abgelehnt* = `account`, obwohl es nach einem Serverfehler aussieht.
   **Grund:** siehe Feldzweck oben — das Konto-Team bearbeitet Aussperrungen, unabhängig
   davon, welches Subsystem den Fehler verursacht.
4. **Bei mehreren Anliegen:** die **erste konkrete Handlungsaufforderung** zählt.
5. **`other` ist kein Papierkorb.** Nur wählen, wenn keine der vier anderen zutrifft.

---

## 3. `priority` — Entscheidungsbaum

Der Reihe nach prüfen. **Die erste zutreffende Zeile gewinnt**, danach wird nicht
weitergelesen.

### Schritt 1 — Frist oder rechtliche Androhung?

Nennt der Kunde eine **Frist, bis zu der er eine Lösung erwartet**, oder droht er
**rechtliche Schritte** an? → **`urgent`**

- *Nicht* darunter fällt verstrichene Zeit ohne Forderung: "seit drei Tagen",
  "zwei Wochen nach dem Liefertermin" ist Schilderung, keine Frist.
- *Nicht* darunter fällt die Berufung auf ein Gesetz ohne Androhung. Ein DSGVO-Antrag
  ist kein Ultimatum.

### Schritt 2 — Behauptet der Kunde einen fehlerhaften Zahlungsvorgang?

Behauptet er, dass **Geld falsch abgeflossen** ist? → **`urgent`**

Darunter fällt: doppelt abgebucht · falscher Betrag abgebucht · abgebucht ohne Bestellung ·
entgegen einer zugesagten Kondition berechnet · Betrag auf der Rechnung stimmt nicht.

**Nicht** darunter fällt **ausbleibendes Geld**: eine überfällige Erstattung, eine nicht
eingelöste Gutschrift. Ärgerlich, aber kein fehlerhafter Vorgang. → weiter prüfen,
endet in aller Regel bei `normal`.

Ob die Behauptung stimmt, ist irrelevant (Grundregel, Abschnitt 0).

### Schritt 3 — Sicherheitsvorfall?

Berichtet der Kunde von einem **Zugriff auf sein Konto, den er nicht selbst veranlasst
hat**, oder äußert er einen konkreten Verdacht darauf? → **`urgent`**

### Schritt 4 — Trifft eines dieser vier zu?

→ **`low`**

- a) **Keine Handlungsaufforderung**: Lob, Feedback, Werbung, Spam
- b) **Reine Auskunftsfrage** zu Produkten oder Abläufen, ohne dass etwas schiefgelaufen ist
- c) **Zusenden eines Dokuments, das bereits existiert**: Rechnungskopie, Beleg
- d) **Änderung von Stammdaten**: Adresse, E-Mail, Zahlungsart

Diese Liste ist **abschließend**. Wenn ein Fall nicht darin steht, ist er nicht `low` —
auch wenn er sich harmlos anfühlt. Eine Kontolöschung ist keine Stammdatenänderung.
Eine Retoure ist keine Auskunftsfrage, auch wenn sie als "wie läuft das ab" formuliert ist.

### Schritt 5 — Sonst

→ **`normal`**. Das ist der Default und deckt die Mehrheit ab.

### Ausdrücklich **kein** Kriterium für `urgent`

- **Tonfall.** Großbuchstaben, Ausrufezeichen, Beleidigungen ändern nichts.
- **Wartezeit**, solange keine Frist gefordert wird.
- **Bestellwert.**
- **Störungs- und Ausfallmeldungen**, egal wie umfassend sie klingen. Ein echter
  Totalausfall wird über Monitoring erkannt, nicht über ein Support-Ticket. Ein 503-Fehler
  auf mehreren Geräten ist `normal`.
- **Persönliche Zugangsprobleme** ohne Sicherheitsverdacht. Vergessenes Passwort = `normal`.

---

## 4. `order_id` — String oder `null`

**Format:** `NL-` gefolgt von genau 6 Ziffern → `NL-482913`

**Normalisierung** (der erwartete Wert steht immer normalisiert im Datensatz):

- Kleinschreibung, fehlender Bindestrich, Leerzeichen werden korrigiert:
  `nl 992003`, `NL992003`, `nl-992003` → alle `NL-992003`

**Regeln:**

| Situation | Erwartung |
|---|---|
| Keine ID in der Nachricht | `null` |
| ID nur in der Signatur / Fußzeile | trotzdem extrahieren |
| Mehrere IDs genannt | die ID, **auf die sich das Anliegen bezieht** |
| Mehrere IDs, Bezug unklar | die **zuerst genannte** |
| Zahl ist erkennbar etwas anderes (Kundennummer, Betrag, PLZ, Datum) | `null` |
| ID-artig, aber falsches Format (`NL-4829`) | `null` |

---

## 5. Erfolgskriterium

Der Harness misst **feldweise**, nicht als Gesamt-Match:

| Feld | Metrik |
|---|---|
| `category` | Accuracy + Confusion-Matrix (welche Kategorien werden verwechselt?) |
| `priority` | Accuracy + separates Recall für `urgent` — ein übersehener Notfall wiegt schwerer als ein Fehlalarm |
| `order_id` | Exact Match nach Normalisierung, getrennt ausgewiesen für Fälle mit und ohne ID |

Zusätzlich: **Parse-Rate** — Anteil der Antworten, die überhaupt valides JSON mit dem
erwarteten Schema sind. Wird gerne vergessen und ist in der Praxis oft der größte Hebel.

Es gibt **kein** Ziel wie "90 % Accuracy". Der Harness dient dem Vergleich von Prompt-
Varianten gegeneinander, nicht dem Erreichen einer absoluten Zahl.

---

## 6. Bekannte Grenzen dieser Spec

- **Tie-Breaker 4** ("erste konkrete Handlungsaufforderung") ist bei verschachtelten
  Sätzen interpretierbar. Bisher ungetestet — im Blind-Review gab es dazu keinen Konflikt,
  aber der Datensatz enthält auch nur einen einzigen Fall (`dev-008`).
- **Die `low`-Liste ist abschließend und dadurch möglicherweise zu eng.** Ein Fall, der
  offensichtlich `low` sein sollte, aber in keine der vier Zeilen passt, ist ein Signal,
  die Liste zu erweitern — nicht, die Regel zu dehnen.
- **`technical` gegen `other`** wurde nie auf die Probe gestellt. `dev-029`
  ("finde nichts auf der Website") streift die Grenze, blieb aber unstrittig.

---

## Änderungshistorie

### 1.1 — nach dem Blind-Review (Vittorio, 32 Fälle)

Vittorio labelte die 32 Fälle unabhängig und ohne Kenntnis der vorgeschlagenen Labels.
Sieben Abweichungen, davon sechs auf drei Spec-Defekte zurückführbar. `order_id` war
32 von 32 identisch — dieser Abschnitt blieb unverändert.

| Änderung | Auslöser | Betroffene Fälle |
|---|---|---|
| **Abschnitt 0 neu**: alle Regeln müssen aus dem Text entscheidbar sein | `dev-014` verlangte Wissen über den Serverzustand, `dev-020` über den Bestellwert | strukturell |
| **Feldzweck von `category`** als Routing-Ziel ergänzt, Tie-Breaker 3 begründet | Tie-Breaker 3 wurde zweimal übergangen, weil sein Sinn nicht dastand | `dev-003`, `dev-022` (Label unverändert) |
| **`priority` von Prosa auf Entscheidungsbaum** umgestellt | zwei Regeln standen korrekt in der Spec, wurden beim Labeln aber nicht gefunden | `dev-020`, `dev-024` |
| **`urgent` bei Zahlungen** an die *Behauptung* des Kunden geknüpft statt an die Tatsache | Konditionsstreit vs. Fehlbuchung war von außen nicht unterscheidbar | `dev-010`, `dev-020` → `urgent` |
| **Ausbleibendes Geld** ausdrücklich von `urgent` ausgenommen | Asymmetrie war ungeregelt, beide Lesarten vertretbar | `dev-025` bleibt `normal` |
| **Ausfallmeldungen** vollständig aus `urgent` entfernt | Kriterium "für alle Nutzer" war nicht entscheidbar | `dev-014` → `normal` |
| **`low`** von der unscharfen Formel "ohne Störung" auf eine **abschließende Liste** umgestellt | "Störung" trug die Last der Abgrenzung nicht | `dev-024` → `normal` |

**Vorgehen dabei:** In allen Fällen wurde zuerst die Regel geändert und erst danach das
Label. `data/blind.jsonl` bleibt eingefroren — die Rohlabels sind die Messung des
Agreements, die adjudizierten Labels stehen in `data/dev.jsonl`.

### 1.0 — Erstfassung
