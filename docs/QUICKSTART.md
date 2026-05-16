# GDk9 Quickstart

Get from zero to your first symbolic energy analysis in under five minutes.

---

## 1. Install

```bash
git clone <repo-url> gdk9
cd gdk9
pip install -e .
gdk9 --version
```

Requires Python 3.9+. No mandatory third-party dependencies for the core CLI.

Optional extras:
```bash
pip install PyYAML          # YAML plugin packs
pip install cryptography    # gdk9 crypto --mode secure
pip install curses          # gdk9 tui (usually bundled with Python)
```

---

## 2. Analyze Text

```bash
gdk9 an "Hello, world!"
```

Output shows energy at document, paragraph, sentence, and word levels — each with a digital-root (DR) value 1–9.

Add `--color` for colorized output:
```bash
gdk9 -C an "Hello, world!"
```

Extended mode includes the 4D vector and harmonic triad counts:
```bash
gdk9 -C an "Hello, world!" -m extended
```

---

## 3. Profile Energy Distribution

```bash
gdk9 -C prof "The quick brown fox jumps over the lazy dog"
```

Shows a histogram of how many characters fall in each energy bucket (1–9), plus the total and digital root.

---

## 4. Attune to a Target Energy

Want your text to have digital root 7?

```bash
gdk9 att "Hello" -t 7 -m append -a ".!?" --include-text
```

GDk9 computes the minimum symbols to append. The `--include-text` flag adds the result to the JSON output.

To write the attuned text back in-place:
```bash
gdk9 att -f notes.txt -t 9 -m intersperse -a ".!?*" -w
```

---

## 5. Explore the DCG

The Directed Cognition Graph classifies each letter by symmetry type and computes SymPhi rest-energy:

```bash
gdk9 -C dcg classify FWEM
```

Find the shortest path between two letters:
```bash
gdk9 dcg shortest F M
```

Check if two words are homotopy-equivalent (same energy + vector distance ≤ tolerance):
```bash
gdk9 dcg homotopy FWEM FeWM
```

---

## 6. Manage Symbols and Rules

```bash
# Add a named symbol
gdk9 sym add ALPHA 5.0

# Define a split rule
gdk9 im split HALVE L R 0.5

# Apply the rule
gdk9 im ap HALVE ALPHA --commit
```

---

## 7. Load a Plugin

```bash
gdk9 pl load ./plugins/harmonic_suite.json
gdk9 pl list
```

Loaded plugins merge their symbol energies and rules into the active session and are remembered for next time.

---

## 8. Interactive TUI

```bash
gdk9 ui --target 7 --allowed ".!?*"
```

Type freely and watch the energy update live. Ctrl-C to exit.

---

## Next Steps

| Topic | Document |
|-------|----------|
| All commands and flags | [CHEATSHEET.md](CHEATSHEET.md) |
| Custom principle files | [CONFIGURATION.md](CONFIGURATION.md) |
| Plugin authoring | [PLUGINS.md](PLUGINS.md) |
| Python library API | [API.md](API.md) |
| Full reference | [HANDBOOK.md](HANDBOOK.md) |
