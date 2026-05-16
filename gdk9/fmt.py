"""gdk9/fmt.py — Pretty terminal output helpers.

Box          Bordered Unicode table with ANSI-aware column widths.
energy_bar   Coloured block-bar for profile histograms.
fmt_class    Symmetry class with colour coding.
fmt_dr       Digital-root integer 1–9 with colour.
fmt_float_e  Float energy value with colour.
fmt_valid    ✓ / ✗ validity mark.
fmt_form     DC / AC form label.
kv           dim-key=bright-value inline pair.
section      Dim rule + bold title header line.
"""
from __future__ import annotations

from typing import List, Optional, Sequence

from .ansi import colorize, strip_ansi


# ── ANSI-aware string helpers ─────────────────────────────────────────────────

def vlen(s: str) -> int:
    """Visible length of *s* (ANSI codes have zero width)."""
    return len(strip_ansi(s))


def vpad(s: str, width: int, align: str = 'l') -> str:
    """Pad *s* to *width* visible characters, preserving embedded ANSI codes."""
    diff = max(0, width - vlen(s))
    if align == 'r':
        return ' ' * diff + s
    if align == 'c':
        lp = diff // 2
        return ' ' * lp + s + ' ' * (diff - lp)
    return s + ' ' * diff


# ── Domain formatters ─────────────────────────────────────────────────────────

_CLASS_COLOR = {
    'idempotent': 'cyan',
    'biphasic':   'yellow',
    'involutive': 'magenta',
    'asymmetric': 'red',
}

_DR_COLOR = {
    1: 'blue',       2: 'blue',
    3: 'cyan',       4: 'green',
    5: 'yellow',     6: 'magenta',
    7: 'red',        8: 'bright_red',
    9: 'bright_white',
}

# Maps DR 1–9 to coloured block chars
_BAR_CHAR = '█'


def fmt_class(cls: str, enabled: bool, *, full: bool = True) -> str:
    """Return symmetry *cls* with class-specific colour."""
    return colorize(cls, _CLASS_COLOR.get(cls), enabled)


def fmt_dr(dr: int, enabled: bool) -> str:
    """Return the digit *dr* (1–9) in its energy colour."""
    return colorize(str(dr), _DR_COLOR.get(dr), enabled)


def fmt_float_e(e: float, enabled: bool) -> str:
    """Format a float SymPhi energy with colour cues."""
    s = f'{e:>9.4f}'
    if not enabled:
        return s
    if e < 0:
        return colorize(s, 'bright_magenta', True)
    if e >= 10:
        return colorize(s, 'bright_white', True)
    return colorize(s, 'cyan', True)


def fmt_valid(v: bool, enabled: bool) -> str:
    if v:
        return colorize('✓', 'bright_green', enabled)
    return colorize('✗', 'bright_red', enabled)


def fmt_form(form: str, enabled: bool) -> str:
    if form == 'upper':
        return colorize('DC', 'bold', enabled)
    return colorize('ac', 'dim', enabled)


def energy_bar(dr: int, count: int, max_count: int,
               bar_width: int = 20, enabled: bool = True) -> str:
    """Return a coloured block-bar proportional to *count* / *max_count*."""
    filled = round(count / max_count * bar_width) if max_count else 0
    bar = _BAR_CHAR * filled
    return colorize(bar, _DR_COLOR.get(dr), enabled)


def kv(key: str, value: str, enabled: bool = True, sep: str = '=') -> str:
    """Return a dim *key* + *value* inline pair.

    If *value* already contains ANSI codes it is passed through unchanged;
    otherwise it is wrapped in bright_white.
    """
    from .ansi import strip_ansi
    v = value if (enabled and strip_ansi(value) != value) else colorize(value, 'bright_white', enabled)
    return colorize(key, 'dim', enabled) + sep + v


def section(title: str, width: int = 44, enabled: bool = True) -> str:
    """A light horizontal rule with a bold centred label.

    Example: ``── classify ─────────────────────``
    """
    label = f' {title} '
    prefix = '── '
    fill = max(0, width - len(prefix) - len(label))
    return (
        colorize(prefix, 'dim', enabled)
        + colorize(title, 'bold', enabled)
        + colorize(' ' + '─' * fill, 'dim', enabled)
    )


# ── Box table ─────────────────────────────────────────────────────────────────

class Box:
    """Unicode-bordered table with ANSI-aware column widths.

    Build the table, then call ``render()`` or ``print()``::

        t = Box(['char', 'class', 'energy'], col_align=['c', 'l', 'r'])
        t.row(['F', fmt_class('asymmetric', True), fmt_float_e(7.0, True)])
        print(t.render())
    """

    _TL = '┌'; _TR = '┐'; _BL = '└'; _BR = '┘'
    _TJ = '┬'; _BJ = '┴'; _LJ = '├'; _RJ = '┤'; _X  = '┼'
    _H  = '─'; _V  = '│'

    def __init__(
        self,
        headers: Sequence[str],
        *,
        col_align: Optional[Sequence[str]] = None,
        enabled: bool = True,
    ) -> None:
        self._h      = list(headers)
        self._rows:  List[List[str]] = []
        self._aligns = list(col_align or ['l'] * len(headers))
        self._divs:  set = set()          # row indices after which to draw ├─┤
        self.enabled = enabled

    # ── Builder API ───────────────────────────────────────────────────────────

    def row(self, cells: Sequence[str]) -> 'Box':
        self._rows.append(list(cells))
        return self

    def divider(self) -> 'Box':
        """Insert a ├───┤ rule after the most recently added row."""
        if self._rows:
            self._divs.add(len(self._rows) - 1)
        return self

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> str:
        en  = self.enabled
        nc  = len(self._h)

        # Compute per-column widths from visible content
        widths = [vlen(h) for h in self._h]
        for row in self._rows:
            for i in range(min(nc, len(row))):
                widths[i] = max(widths[i], vlen(row[i]))

        def bd(s: str) -> str:
            return colorize(s, 'dim', en) if en else s

        def hsep(left: str, mid: str, right: str) -> str:
            segs = (bd(self._H * (w + 2)) for w in widths)
            return bd(left) + bd(mid).join(segs) + bd(right)

        def render_row(cells: List[str]) -> str:
            parts: List[str] = []
            for i in range(nc):
                content = cells[i] if i < len(cells) else ''
                a = self._aligns[i] if i < len(self._aligns) else 'l'
                parts.append(' ' + vpad(content, widths[i], a) + ' ')
            return bd(self._V) + bd(self._V).join(parts) + bd(self._V)

        lines: List[str] = []
        lines.append(hsep(self._TL, self._TJ, self._TR))
        lines.append(render_row([colorize(h, 'bold', en) for h in self._h]))
        lines.append(hsep(self._LJ, self._X, self._RJ))

        for i, row in enumerate(self._rows):
            lines.append(render_row(row))
            if i in self._divs and i < len(self._rows) - 1:
                lines.append(hsep(self._LJ, self._X, self._RJ))

        lines.append(hsep(self._BL, self._BJ, self._BR))
        return '\n'.join(lines)

    def __str__(self) -> str:
        return self.render()

    def print(self) -> None:
        print(self.render())
