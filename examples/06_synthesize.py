"""Example 06 — synthesize: build a sigil from an energy profile.

synthesize takes a word and renders a bordered sigil with per-letter
DR coloring, the total SymPhi energy, and the digital root.
"""
import subprocess, sys

def run(*args):
    result = subprocess.run(
        [sys.executable, "-m", "gdk9.cli", *args],
        capture_output=True, text=True,
    )
    print(result.stdout or result.stderr)

words = ["FWEM", "dark", "swan", "protocol"]

for word in words:
    print(f"=== synthesize: {word} ===")
    run("--color", "synthesize", word)
    print()
