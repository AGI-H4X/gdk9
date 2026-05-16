#!/usr/bin/env python3
"""Side-by-side energy histogram comparison of two inputs.

Usage:
    python scripts/profile_compare.py "text one" "text two"
    python scripts/profile_compare.py -f file_a.txt -g file_b.txt
    python scripts/profile_compare.py "hello" "world" --format json

Shows a unified diff of the DR histogram bins, totals, and digital roots.
Highlights where the two distributions diverge.
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
from gdk9.energy import energy_profile, string_energy, harmonic_triads


BAR_WIDTH = 16
TRIAD_COLORS = {1: "\033[91m", 4: "\033[91m", 7: "\033[91m",   # root: red
                2: "\033[96m", 5: "\033[96m", 8: "\033[96m",   # wave: cyan
                3: "\033[93m", 6: "\033[93m", 9: "\033[93m"}  # peak: yellow
RESET = "\033[0m"


def _bar(count: int, max_count: int, dr: int, use_color: bool) -> str:
    filled = int(BAR_WIDTH * count / max_count) if max_count else 0
    bar = "█" * filled + "░" * (BAR_WIDTH - filled)
    if use_color and count > 0:
        col = TRIAD_COLORS.get(dr, "")
        return col + bar + RESET
    return bar


def compare(text_a: str, text_b: str, label_a: str, label_b: str, principle, use_color: bool) -> dict:
    prof_a = energy_profile(text_a, principle)
    prof_b = energy_profile(text_b, principle)
    tot_a, dr_a = string_energy(text_a, principle)
    tot_b, dr_b = string_energy(text_b, principle)
    harm_a = harmonic_triads(text_a, principle)
    harm_b = harmonic_triads(text_b, principle)

    max_cnt = max(
        max(int(v) for v in prof_a.values()),
        max(int(v) for v in prof_b.values()),
        1,
    )

    rows = []
    for i in range(1, 10):
        ca = int(prof_a[str(i)])
        cb = int(prof_b[str(i)])
        diff = cb - ca
        diff_s = f"{diff:+d}" if diff != 0 else "—"
        rows.append((i, ca, cb, diff_s))

    return {
        "label_a": label_a,
        "label_b": label_b,
        "profile_a": prof_a,
        "profile_b": prof_b,
        "total_a": tot_a, "dr_a": dr_a,
        "total_b": tot_b, "dr_b": dr_b,
        "harmonics_a": harm_a,
        "harmonics_b": harm_b,
        "rows": rows,
        "max_count": max_cnt,
    }


def print_table(data: dict, use_color: bool) -> None:
    la, lb = data["label_a"], data["label_b"]
    hdr_a = (la[:18] + "…") if len(la) > 18 else la
    hdr_b = (lb[:18] + "…") if len(lb) > 18 else lb

    sep = "─" * (6 + BAR_WIDTH + 1 + 6 + 4 + 6 + BAR_WIDTH + 1 + 6)
    print(f"  DR   {'CNT':>4}  {'─' * BAR_WIDTH}  {hdr_a:<18}   {'CNT':>4}  {'─' * BAR_WIDTH}  {hdr_b:<18}   DIFF")
    print(sep)

    for (i, ca, cb, diff_s) in data["rows"]:
        bar_a = _bar(ca, data["max_count"], i, use_color)
        bar_b = _bar(cb, data["max_count"], i, use_color)
        dr_s = str(i)
        if use_color:
            col = TRIAD_COLORS.get(i, "")
            dr_s = col + dr_s + RESET
        changed = (ca != cb)
        diff_col = ("\033[93m" if changed else "") if use_color else ""
        diff_end = RESET if (use_color and changed) else ""
        print(f"  {dr_s}    {ca:>4}  {bar_a}  {ca:<6}   {cb:>4}  {bar_b}  {cb:<6}   {diff_col}{diff_s:>5}{diff_end}")

    print(sep)
    ta, da = data["total_a"], data["dr_a"]
    tb, db = data["total_b"], data["dr_b"]
    tdiff = tb - ta
    print(f"  total  {ta:>6}   dr={da}           {tb:>6}   dr={db}           Δ={tdiff:+d}")

    ha, hb = data["harmonics_a"], data["harmonics_b"]
    print(f"  root   {ha['root']:>6}                   {hb['root']:>6}")
    print(f"  wave   {ha['wave']:>6}                   {hb['wave']:>6}")
    print(f"  peak   {ha['peak']:>6}                   {hb['peak']:>6}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Side-by-side GDk9 energy profile comparison.")
    p.add_argument("text_a", nargs="?", help="First input text")
    p.add_argument("text_b", nargs="?", help="Second input text")
    p.add_argument("--file-a", "-f", help="First input file")
    p.add_argument("--file-b", "-g", help="Second input file")
    p.add_argument("--label-a", "-A", help="Label for first input")
    p.add_argument("--label-b", "-B", help="Label for second input")
    p.add_argument("--principle", "-P", help="Principle file")
    p.add_argument("--format", "-F", choices=["table", "json"], default="table")
    p.add_argument("--no-color", action="store_true")
    args = p.parse_args(argv)

    if args.file_a:
        text_a = Path(args.file_a).read_text(encoding="utf-8")
        label_a = args.label_a or args.file_a
    elif args.text_a:
        text_a = args.text_a
        label_a = args.label_a or repr(args.text_a[:20])
    else:
        print("error: provide text_a or --file-a", file=sys.stderr)
        return 2

    if args.file_b:
        text_b = Path(args.file_b).read_text(encoding="utf-8")
        label_b = args.label_b or args.file_b
    elif args.text_b:
        text_b = args.text_b
        label_b = args.label_b or repr(args.text_b[:20])
    else:
        print("error: provide text_b or --file-b", file=sys.stderr)
        return 2

    principle = load_principle(args.principle)
    use_color = not args.no_color and sys.stdout.isatty()

    data = compare(text_a, text_b, label_a, label_b, principle, use_color)

    if args.format == "json":
        data.pop("rows", None)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print_table(data, use_color)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
