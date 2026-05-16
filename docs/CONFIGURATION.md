# GDk9 Configuration

---

## Principle Files

A principle defines how energy is computed: the letter mode, number mode, per-category weights, and symbol energy mapping.

### Loading Order

1. `--principle / -P FILE` flag → load from that file.
2. `gdk9/data/official.json` if it exists (install via `gdk9 prin install --file my.json`).
3. Built-in Ninefold Grid (`gdk9/data/ninefold.json`).

### JSON Schema

```json
{
  "name": "My Principle",
  "description": "Optional free-text description",
  "letter_mode": "a1z26",
  "number_mode": "digital_root",
  "normalize_zero_to_nine": true,
  "weights": {
    "letter": 1,
    "digit":  1,
    "symbol": 1
  },
  "symbol_energy": {
    ".":  1,
    ",":  2,
    "!":  3,
    "?":  4,
    ":":  5,
    ";":  6,
    "-":  7,
    "_":  8,
    "*":  9
  }
}
```

### Field Reference

| Field | Values | Default | Description |
|-------|--------|---------|-------------|
| `letter_mode` | `a1z26` \| `unicode` | `a1z26` | A1Z26: A=1…Z=26. Unicode: raw code point. |
| `number_mode` | `digital_root` \| `raw` | `digital_root` | How digit characters are valued. |
| `normalize_zero_to_nine` | bool | `true` | Map DR=0 to 9 (full cycle). |
| `weights.letter` | int ≥ 1 | 1 | Multiplier applied after DR to letter energies. |
| `weights.digit` | int ≥ 1 | 1 | Multiplier for digit energies. |
| `weights.symbol` | int ≥ 1 | 1 | Multiplier for symbol energies. |
| `symbol_energy` | `{char: int}` | see ninefold.json | Override/extend symbol table. |

### YAML Format

```yaml
name: My Principle
letter_mode: a1z26
number_mode: digital_root
normalize_zero_to_nine: true
weights:
  letter: 1
  digit: 1
  symbol: 1
symbol_energy:
  ".": 1
  "!": 3
```

### Validate a Principle

```bash
gdk9 prin validate --file my_principle.json
# ok  (exit 0) or  invalid: <reason>  (exit 2)
```

### Install as Default

```bash
gdk9 prin install --file my_principle.json
# Writes to gdk9/data/official.json — becomes the default for this install
```

---

## State File

Stores named symbols and implication rules between sessions.

**Default location:** `~/.gdk9/state.json`

**Override:** `--state / -S path` flag or `-S` in the relevant subcommand.

### Structure

```json
{
  "symbols": {
    "ALPHA": {
      "energy": 5.0,
      "ts": 1716000000.0
    }
  },
  "rules": {
    "HALVE": {
      "name": "HALVE",
      "type": "split",
      "arity": 2,
      "params": {"out_a": "L", "out_b": "R", "ratio": 0.5},
      "ts": 1716000000.0
    }
  }
}
```

`ts` is a Unix timestamp used by the CRDT merge (last-write-wins per key).

### Reset State

```bash
gdk9 reset --yes              # clear all symbols and rules
gdk9 reset --rules-only --yes # keep symbols, clear rules
gdk9 reset --symbols-only --yes
```

---

## Plugin Auto-Boot

**Config file:** `~/.gdk9/plugins.json`

```json
{
  "enabled": {
    "my_pack": "/path/to/plugins/my_pack.yaml"
  }
}
```

Enabled plugins are loaded at every CLI startup. Their `symbol_energy` is merged into the active principle and their rules/symbols are seeded into state (if not already present).

### Manage Auto-Boot

```bash
gdk9 pl load ./plugins/pack.yaml          # load + enable
gdk9 pl load ./plugins/pack.yaml --no-enable  # load only this session
gdk9 pl enable my_pack                    # enable an already-loaded pack
gdk9 pl disable my_pack                   # remove from auto-boot
gdk9 reset --plugins --yes                # wipe ~/.gdk9/plugins.json
```

---

## Plugin Search Paths

GDk9 searches for plugins in order:

1. `./plugins/` — project-local directory.
2. `~/.gdk9/plugins/` — user directory.

Plugins can be referenced by name (stem without extension) or by full path.

---

## Environment Variables

| Variable | Effect |
|----------|--------|
| `GDK9_DEBUG=1` | Enable debug logging (equivalent to `--debug`) |
| `NO_COLOR=1` | Disable ANSI color (standard convention) |

---

## Substitution Profiles

Used by `gdk9 att --method substitute` and `--method edit`.

**File format:**
```json
{
  "subs": {
    "i": ["1", "!"],
    "s": ["$", "5"],
    "e": ["3"],
    "a": ["4", "@"],
    ",": [";", ":"]
  },
  "allowed_inserts": ".!?+"
}
```

**Generate from active principle:**
```bash
gdk9 subs generate -o subs.json
```

**Use:**
```bash
gdk9 att "message" -t 7 -m substitute --subs-file subs.json
```

---

## Per-Run Principle Merging (Plugins)

When a plugin is loaded or auto-booted, its `symbol_energy` is merged into the active principle **for that run only** (the source `ninefold.json` / `official.json` is never modified). This allows plugins to extend the symbol table without permanently altering the base principle.

To permanently extend the default principle, edit `official.json` directly or use `prin install`.
