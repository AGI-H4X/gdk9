```markdown
# gdk9

Short description of what gdk9 is and does.

## Recommended repo layout

- pyproject.toml               - build metadata and declared deps
- requirements.txt             - runtime deps (optional if using pyproject)
- requirements-dev.txt         - developer tooling and test deps
- src/gdk9/                    - package source
- examples/plugins/            - example plugins (not installed as entry-points)
- tests/                       - pytest tests
- .github/workflows/ci.yml     - CI for running tests

## Plugin system

This repository uses an entry-point group `gdk9.plugins` (see `pyproject.toml`) to load third-party plugins.
Plugins should expose a class with `setup(config)` and `run(...)` methods.

To test locally without installing:
- Use the `examples/plugins/example_plugin.py` as a reference.
- You can import and instantiate plugin classes directly, or install a package that declares an entry-point.

## Development

- Install dev dependencies: `pip install -r requirements-dev.txt` or `pip install .[dev]`
- Use `pre-commit` for formatting and linting
- Run tests: `pytest`
```