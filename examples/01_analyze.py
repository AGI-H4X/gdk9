"""Example 01 — analyze: break text into energy units.

gdk9 analyze decomposes text from document → paragraph → sentence → word,
reporting the A1Z26 digital-root energy at each level.
"""
import subprocess, sys, os

_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def run(*args):
    result = subprocess.run(
        [sys.executable, "-m", "gdk9.cli", *args],
        capture_output=True, text=True,
        cwd=_ROOT,
    )
    print(result.stdout or result.stderr)

# Basic analysis
print("=== analyze a phrase ===")
run("--color", "analyze", "Signal 123 ehdxkcit 3245768")

# Table format
print("=== analyze — table format ===")
run("--color", "analyze", "FWEM dark swan protocol", "--format", "table")

# Compare two phrases
print("=== compare two strings ===")
run("--color", "compare", "dark swan", "dark swan protocol")
