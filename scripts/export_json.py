#!/usr/bin/env python3
"""Full JSON export for a single input: analysis, profile, assign, DCG classify.

Usage:
    python scripts/export_json.py "Your text here"
    python scripts/export_json.py -f input.txt
    python scripts/export_json.py "text" --sections analysis,profile,assign,dcg
    python scripts/export_json.py "text" -o output.json

Output is a single JSON object with keys for each requested section.
Pipe into jq, save to file, or feed downstream tools.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _setup_path() -> None:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_setup_path()

from gdk9.principles import load_principle
from gdk9.energy import (
    analyze_text, energy_profile, string_energy,
    vector_energy, harmonic_triads, char_energy,
)
from gdk9.dcg import symmetry_class, sym_energy, vectorize


ALL_SECTIONS = ["analysis", "profile", "assign", "dcg", "vector", "harmonics"]


def export(text: str, principle, sections: list[str]) -> dict:
    out: dict = {"input": text}

    if "analysis" in sections:
        result = analyze_text(text, principle)
        out["analysis"] = {k: [u.__dict__ for u in v] for k, v in result.items()}

    if "profile" in sections:
        prof = energy_profile(text, principle)
        total, dr = string_energy(text, principle)
        out["profile"] = {"bins": prof, "total": total, "dr": dr}

    if "assign" in sections:
        out["assign"] = [
            {"char": ch, "energy": char_energy(ch, principle)}
            for ch in text if ch != "\n"
        ]

    if "dcg" in sections:
        letters = [c for c in text if c.isalpha()]
        out["dcg"] = [
            {
                "char": ch,
                "class": symmetry_class(ch),
                "energy": round(sym_energy(ch), 6),
                "vector": [round(x, 6) for x in vectorize(ch)],
                "form": "DC" if ch.isupper() else "AC",
            }
            for ch in letters
        ]

    if "vector" in sections:
        out["vector"] = vector_energy(text, principle)

    if "harmonics" in sections:
        out["harmonics"] = harmonic_triads(text, principle)

    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Full JSON export for a single GDk9 input.")
    p.add_argument("text", nargs="?", help="Inline text")
    p.add_argument("--file", "-f", help="Read text from file")
    p.add_argument("--principle", "-P", help="Principle file")
    p.add_argument(
        "--sections", "-s",
        default=",".join(ALL_SECTIONS),
        help=f"Comma-separated sections: {','.join(ALL_SECTIONS)} (default: all)",
    )
    p.add_argument("--out", "-o", help="Output file (default: stdout)")
    p.add_argument("--indent", type=int, default=2, help="JSON indent (default: 2)")
    args = p.parse_args(argv)

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("error: empty input", file=sys.stderr)
        return 2

    principle = load_principle(args.principle)
    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    unknown = [s for s in sections if s not in ALL_SECTIONS]
    if unknown:
        print(f"error: unknown sections: {unknown}. Valid: {ALL_SECTIONS}", file=sys.stderr)
        return 2

    payload = export(text, principle, sections)
    output = json.dumps(payload, indent=args.indent, ensure_ascii=False)

    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        print(args.out)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
