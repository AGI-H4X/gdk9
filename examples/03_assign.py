"""Example 03 — assign: per-character energy breakdown.

assign lists every character with its individual energy value and DR,
useful for auditing which letters drive the total energy of a word.
"""
import subprocess, sys

def run(*args):
    result = subprocess.run(
        [sys.executable, "-m", "gdk9.cli", *args],
        capture_output=True, text=True,
    )
    print(result.stdout or result.stderr)

print("=== assign: FWEM ===")
run("--color", "assign", "FWEM")

print("=== assign: dark swan ===")
run("--color", "assign", "dark swan")
