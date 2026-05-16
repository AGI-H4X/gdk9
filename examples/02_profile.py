"""Example 02 — profile: energy histogram and DR distribution.

profile shows how energy is distributed across digital roots 1-9,
rendered as a coloured block-bar chart.
"""
import subprocess, sys

def run(*args):
    result = subprocess.run(
        [sys.executable, "-m", "gdk9.cli", *args],
        capture_output=True, text=True,
    )
    print(result.stdout or result.stderr)

texts = [
    "The quick brown fox jumps over the lazy dog",
    "FWEM",
    "dark swan protocol identity",
]

for text in texts:
    print(f'=== profile: {text!r} ===')
    run("--color", "profile", text)
    print()
