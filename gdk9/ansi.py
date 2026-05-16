from __future__ import annotations

import os
import re
import sys

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

_CODES: dict[str, str] = {
  # styles
  "bold":           "\033[1m",
  "dim":            "\033[2m",
  "italic":         "\033[3m",
  "underline":      "\033[4m",
  "reverse":        "\033[7m",
  # standard colours
  "red":            "\033[31m",
  "green":          "\033[32m",
  "yellow":         "\033[33m",
  "blue":           "\033[34m",
  "magenta":        "\033[35m",
  "cyan":           "\033[36m",
  "white":          "\033[37m",
  # bright variants
  "bright_black":   "\033[90m",
  "bright_red":     "\033[91m",
  "bright_green":   "\033[92m",
  "bright_yellow":  "\033[93m",
  "bright_blue":    "\033[94m",
  "bright_magenta": "\033[95m",
  "bright_cyan":    "\033[96m",
  "bright_white":   "\033[97m",
}

_RESET = "\033[0m"


def supports_color() -> bool:
  if os.getenv("NO_COLOR") == "1":
    return False
  term = os.getenv("TERM", "")
  if term in ("dumb", ""):
    return False
  return sys.stdout.isatty()


def colorize(text: str, color: str | None, enabled: bool) -> str:
  if not enabled or not color:
    return text
  code = _CODES.get(color, "")
  return f"{code}{text}{_RESET}" if code else text


def strip_ansi(s: str) -> str:
  """Remove all ANSI escape codes from *s*."""
  return _ANSI_RE.sub("", s)

