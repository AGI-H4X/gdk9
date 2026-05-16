"""Example 05 — tokenize: split text by symbolic energy delimiters.

Delimiters are characters whose symbol-energy equals the requested level.
With -F table the output includes per-token DR, energy totals, and a
metrics footer (DR histogram, top tokens, class breakdown).
"""
import subprocess, sys

def run(*args):
    result = subprocess.run(
        [sys.executable, "-m", "gdk9.cli", *args],
        capture_output=True, text=True,
    )
    print(result.stdout or result.stderr)

text = "alpha|beta:gamma/delta=epsilon"

print("=== tokenize at energy-1 delimiters (table) ===")
run("--color", "tokenize", text, "--energy", "1", "-F", "table")

print("=== tokenize JSON payload ===")
run("tokenize", "FWEM dark-swan protocol", "-F", "json")
