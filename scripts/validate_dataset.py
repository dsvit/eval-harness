#!/usr/bin/env python3
"""
Validiert einen Eval-Datensatz gegen spec/task_spec.md.

Warum das existiert: ein Datensatz ist Code. Ein Tippfehler in einem Label verfaelscht
jede spaetere Messung still und leise. Diesen Check laesst man vor jedem Eval-Lauf
durchlaufen, nicht nur einmal am Anfang.

Aufruf:  python3 scripts/validate_dataset.py data/dev.jsonl
Exit 0 = sauber, Exit 1 = Fehler gefunden.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

CATEGORIES = {"billing", "technical", "account", "shipping", "other"}
PRIORITIES = {"low", "normal", "urgent"}
DIFFICULTIES = {"easy", "medium", "hard"}
ORDER_ID_RE = re.compile(r"^NL-\d{6}$")
ID_RE = re.compile(r"^dev-\d{3}$")


def validate(path: Path) -> tuple[list[str], list[dict]]:
    errors: list[str] = []
    rows: list[dict] = []
    seen_ids: set[str] = set()

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue

        def err(msg: str) -> None:
            errors.append(f"Zeile {lineno}: {msg}")

        try:
            row = json.loads(raw)
        except json.JSONDecodeError as e:
            err(f"kein valides JSON ({e.msg} an Position {e.pos})")
            continue

        # --- Top-Level-Struktur ---
        missing = {"id", "input", "expected", "meta"} - row.keys()
        if missing:
            err(f"fehlende Felder: {sorted(missing)}")
            continue
        extra = row.keys() - {"id", "input", "expected", "meta"}
        if extra:
            err(f"unerwartete Felder: {sorted(extra)}")

        rid = row["id"]
        if not ID_RE.match(str(rid)):
            err(f"id '{rid}' entspricht nicht dem Muster dev-NNN")
        if rid in seen_ids:
            err(f"doppelte id '{rid}'")
        seen_ids.add(rid)

        if not isinstance(row["input"], str) or not row["input"].strip():
            err("input ist leer oder kein String")

        # --- expected ---
        exp = row["expected"]
        if not isinstance(exp, dict):
            err("expected ist kein Objekt")
            continue
        if exp.keys() != {"category", "priority", "order_id"}:
            err(f"expected hat falsche Schluessel: {sorted(exp.keys())}")
            continue

        if exp["category"] not in CATEGORIES:
            err(f"unbekannte category '{exp['category']}'")
        if exp["priority"] not in PRIORITIES:
            err(f"unbekannte priority '{exp['priority']}'")

        oid = exp["order_id"]
        if oid is not None:
            if not isinstance(oid, str) or not ORDER_ID_RE.match(oid):
                err(f"order_id '{oid}' ist nicht normalisiert (erwartet NL-######)")
            elif oid.lower().replace("-", "").replace(" ", "") not in \
                    row["input"].lower().replace("-", "").replace(" ", ""):
                # Faengt den haeufigsten Labelfehler: ID getippt, die im Text gar nicht steht.
                err(f"order_id '{oid}' kommt im input nicht vor")

        # --- meta ---
        meta = row["meta"]
        if not isinstance(meta, dict):
            err("meta ist kein Objekt")
            continue
        if meta.get("difficulty") not in DIFFICULTIES:
            err(f"unbekannte difficulty '{meta.get('difficulty')}'")
        if not isinstance(meta.get("tags"), list) or not meta["tags"]:
            err("tags fehlen oder sind leer")
        if not str(meta.get("note", "")).strip():
            err("note fehlt — jeder Fall braucht eine Begruendung")

        rows.append(row)

    return errors, rows


def report(rows: list[dict]) -> None:
    n = len(rows)
    print(f"\n{n} Faelle geladen\n")

    def dist(label: str, values: list, order: list | None = None) -> None:
        c = Counter(values)
        keys = order or sorted(c, key=lambda k: -c[k])
        print(f"  {label}")
        for k in keys:
            cnt = c.get(k, 0)
            bar = "#" * round(cnt / n * 40)
            print(f"    {str(k):<10} {cnt:>3}  {cnt / n:>5.0%}  {bar}")
        print()

    dist("category", [r["expected"]["category"] for r in rows])
    dist("priority", [r["expected"]["priority"] for r in rows], ["urgent", "normal", "low"])
    dist("difficulty", [r["meta"]["difficulty"] for r in rows], ["easy", "medium", "hard"])
    dist("order_id", ["vorhanden" if r["expected"]["order_id"] else "null" for r in rows])

    tags = Counter(t for r in rows for t in r["meta"]["tags"])
    print("  tags")
    for t, c in tags.most_common():
        print(f"    {t:<22} {c}")
    print()

    # Warnungen: keine Fehler, aber Dinge, die eine Messung unbrauchbar machen koennen.
    warn = []
    for field, allowed in (("category", CATEGORIES), ("priority", PRIORITIES)):
        counts = Counter(r["expected"][field] for r in rows)
        for value in allowed:
            if counts.get(value, 0) < 3:
                warn.append(
                    f"{field}='{value}' hat nur {counts.get(value, 0)} Faelle — "
                    f"Metriken fuer diese Klasse sind statistisch wertlos"
                )
    if warn:
        print("  Warnungen")
        for w in warn:
            print(f"    ! {w}")
        print()


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/dev.jsonl")
    if not path.exists():
        print(f"Datei nicht gefunden: {path}", file=sys.stderr)
        return 1

    errors, rows = validate(path)
    if errors:
        print(f"\n{len(errors)} Fehler in {path}:\n", file=sys.stderr)
        for e in errors:
            print(f"  x {e}", file=sys.stderr)
        return 1

    print(f"\nSchema OK: {path}")
    report(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
