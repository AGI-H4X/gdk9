"""Example 04 — DCG: Directed Cognition Graph.

The DCG models letters as nodes in a directed graph with three edge types:
  DC↔AC   uppercase ↔ lowercase (cost 0.5 / 2.0)
  within  all-pairs within symmetry class (cost 1.0)
  cross   energy cycle asym → biph → idemp → invol → asym (cost 2.0)

Demonstrates: classify, path, homotopy, shortest, vector, info.
"""
import subprocess, sys

def run(*args):
    result = subprocess.run(
        [sys.executable, "-m", "gdk9.cli", *args],
        capture_output=True, text=True,
    )
    print(result.stdout or result.stderr)

# Symmetry class of individual letters
print("=== dcg classify ===")
run("--color", "dcg", "classify", "FWEM")

# Full word path — symmetry class + energy per letter
print("=== dcg path: FWEM ===")
run("--color", "dcg", "path", "FWEM")

# Shortest path between two nodes
print("=== dcg shortest: F → M ===")
run("--color", "dcg", "shortest", "F", "M")

# Homotopy equivalence: same letters reordered
print("=== dcg homotopy: FWEM vs MWEF ===")
run("--color", "dcg", "homotopy", "FWEM", "MWEF")

# 4D vector encoding
print("=== dcg vector: FWEM ===")
run("--color", "dcg", "vector", "FWEM")

# Graph info
print("=== dcg info ===")
run("--color", "dcg", "info")
