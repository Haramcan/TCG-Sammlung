#!/usr/bin/env python3
"""Holt die aktuelle Cardmarket-Preisliste und schreibt kompakte Preisdateien für die App.

Aufruf: python3 tools/build_prices.py ZIELORDNER
Erzeugt ZIELORDNER/dbfw.json und ZIELORDNER/op.json:
  {"d": "2026-11-02", "p": {"FB02-001": 0.07, "FB02-001_p1": [30.0, 1], ...}}
  [preis, 1] bedeutet: nur günstigstes Angebot, keine Verkäufe ("ab …").
Läuft täglich über GitHub Actions (.github/workflows/preise.yml) und landet auf dem Branch "preise".
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_data as b  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "preise")
    os.makedirs(out, exist_ok=True)
    for game, gid in (("dbfw", 13), ("op", 18)):
        data = json.load(open(os.path.join(ROOT, "data", f"{game}.json"), encoding="utf-8"))
        cards = data["cards"]
        for c in cards:
            for k in ("eur", "eurLow", "cm"):
                c.pop(k, None)
        date = b.add_cardmarket(cards, gid)
        if not date:
            print(f"{game}: keine Preise geladen", file=sys.stderr)
            continue
        prices = {c["id"]: ([c["eur"], 1] if c.get("eurLow") else c["eur"]) for c in cards if "eur" in c}
        with open(os.path.join(out, f"{game}.json"), "w", encoding="utf-8") as f:
            json.dump({"d": date, "p": prices}, f, ensure_ascii=False, separators=(",", ":"))
        print(f"{game}: {len(prices)} Preise, Stand {date}")


if __name__ == "__main__":
    main()
