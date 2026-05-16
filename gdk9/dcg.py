"""Directed Cognition Graph (DCG) for GDk9.

Nodes: all 52 alphabetic characters (A–Z, a–z), each labelled with its
symmetry class, SymPhi rest-energy, and 4D vector.

Edge types and costs
--------------------
  Uppercase ↔ lowercase   DC ↔ AC form conversion        cost 1 (→) / 2 (←)
  Within-class all-pairs  same symmetry class, same case  cost 1
  Cross-class cycle        asym → biph → idemp → invol
                           → asym (both cases)             cost 2

The cross-class cycle formalises the energy-flow circuit from the whitepaper.
F → E (asymmetric → biphasic) is the canonical DC→AC choice-point.

Energy model
------------
SymPhi rest-energy uses positional algebra (not digital root):
  idempotent   E = pos          (1–26)
  biphasic     E = sin(pos)
  involutive   E = 1 / pos
  asymmetric   E = pos + 1

4D vector per character: [pos, type_id, √|E|, sin(pos·π/26)]
"""
from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Tuple

# ── Symmetry sets (whitepaper §2.2) ──────────────────────────────────────────

_IDEMP = frozenset('AHIMOTUVWXY')   # idempotent:  x²=x  (11 letters)
_BIPH  = frozenset('BCDEK')         # biphasic:    x²=f(x) (5)
_INVOL = frozenset('NSZ')           # involutive:  x²=1    (3)
_ASYM  = frozenset('FGJLPQR')       # asymmetric:  x²≠x,1  (7)

_CLASS_UPPER: Dict[str, List[str]] = {
    'idempotent': sorted(_IDEMP),
    'biphasic':   sorted(_BIPH),
    'involutive': sorted(_INVOL),
    'asymmetric': sorted(_ASYM),
}
_CLASS_LOWER: Dict[str, List[str]] = {
    sc: [c.lower() for c in letters]
    for sc, letters in _CLASS_UPPER.items()
}

_SYM_ID: Dict[str, int] = {
    'idempotent': 1,
    'biphasic':   2,
    'involutive': 3,
    'asymmetric': 4,
}

# ── Per-character functions ───────────────────────────────────────────────────

def symmetry_class(char: str) -> str:
    """Return the symmetry class for any alphabetic character.

    Classification is determined by the uppercase form, so 'f' and 'F'
    both return 'asymmetric'.  Non-alpha characters fall back to 'asymmetric'.
    """
    u = char.upper()
    if u in _IDEMP:  return 'idempotent'
    if u in _BIPH:   return 'biphasic'
    if u in _INVOL:  return 'involutive'
    if u in _ASYM:   return 'asymmetric'
    return 'asymmetric'


def sym_energy(char: str) -> float:
    """SymPhi rest-energy for a single alphabetic character.

    Uses positional algebra rather than digital root so that energy values
    reflect topological shape and continuous symmetry properties.
    """
    if not char.isalpha():
        return 0.0
    pos = ord(char.upper()) - ord('A') + 1   # 1–26
    sc = symmetry_class(char)
    if sc == 'idempotent':  return float(pos)
    if sc == 'biphasic':    return math.sin(pos)
    if sc == 'involutive':  return 1.0 / pos
    return float(pos + 1)                    # asymmetric


def vectorize(char: str) -> Tuple[float, float, float, float]:
    """4D vector [pos, type_id, √|E|, sin(pos·π/26)] per the whitepaper."""
    if not char.isalpha():
        return (0.0, 0.0, 0.0, 0.0)
    pos   = ord(char.upper()) - ord('A') + 1
    sc    = symmetry_class(char)
    tid   = float(_SYM_ID.get(sc, 0))
    e     = sym_energy(char)
    theta = pos * math.pi / 26.0
    return (float(pos), tid, math.sqrt(abs(e)), math.sin(theta))


def word_sym_energy(word: str) -> float:
    """Sum of SymPhi rest-energies for all alphabetic characters in *word*."""
    return sum(sym_energy(c) for c in word if c.isalpha())


def word_vector(word: str) -> Tuple[float, float, float, float]:
    """Sum of 4D character vectors for all alphabetic characters in *word*."""
    v = [0.0, 0.0, 0.0, 0.0]
    for c in word:
        if c.isalpha():
            cv = vectorize(c)
            for i in range(4):
                v[i] += cv[i]
    return (v[0], v[1], v[2], v[3])


# ── Graph ─────────────────────────────────────────────────────────────────────

class DCG:
    """Directed Cognition Graph over the 52-letter alphabet.

    Internal representation: adjacency dict ``{src: {dst: weight}}``.
    All public mutation happens through :func:`build_dcg` / :func:`get_dcg`.
    """

    __slots__ = ('_adj', '_nodes')

    def __init__(self) -> None:
        self._adj:   Dict[str, Dict[str, float]] = {}
        self._nodes: Dict[str, Dict]             = {}

    # ── Internal builders ─────────────────────────────────────────────────────

    def _ensure_node(self, char: str) -> None:
        if char not in self._nodes:
            self._nodes[char] = {
                'class':  symmetry_class(char),
                'energy': sym_energy(char),
                'vector': vectorize(char),
                'form':   'upper' if char.isupper() else 'lower',
            }
            self._adj[char] = {}

    def _add_edge(self, src: str, dst: str, weight: float = 1.0) -> None:
        self._ensure_node(src)
        self._ensure_node(dst)
        if weight < self._adj[src].get(dst, float('inf')):
            self._adj[src][dst] = weight

    # ── Inspection ────────────────────────────────────────────────────────────

    def node_data(self, char: str) -> Dict:
        """Return a copy of the metadata dict for *char*."""
        return dict(self._nodes.get(char, {}))

    def has_edge(self, src: str, dst: str) -> bool:
        return dst in self._adj.get(src, {})

    def edge_weight(self, src: str, dst: str) -> Optional[float]:
        return self._adj.get(src, {}).get(dst)

    def successors(self, node: str) -> List[str]:
        return list(self._adj.get(node, {}).keys())

    def predecessors(self, node: str) -> List[str]:
        return [n for n, dsts in self._adj.items() if node in dsts]

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return sum(len(dsts) for dsts in self._adj.values())

    def edge_count_by_type(self) -> Dict[str, int]:
        """Count edges grouped by source-class → dest-class label."""
        counts: Dict[str, int] = {}
        for src, dsts in self._adj.items():
            sc = self._nodes[src]['class']
            sf = self._nodes[src]['form']
            for dst in dsts:
                dc = self._nodes[dst]['class']
                df = self._nodes[dst]['form']
                if sf != df:
                    label = 'dc_ac'
                elif sc == dc:
                    label = f'within_{sc}'
                else:
                    label = f'{sc}_to_{dc}'
                counts[label] = counts.get(label, 0) + 1
        return counts

    # ── Algorithms ────────────────────────────────────────────────────────────

    def shortest_path(self, src: str, dst: str) -> Optional[List[str]]:
        """Dijkstra shortest path from *src* to *dst*.

        Returns the ordered node list, or ``None`` if unreachable.
        """
        if src not in self._nodes or dst not in self._nodes:
            return None
        dist: Dict[str, float] = {n: float('inf') for n in self._nodes}
        prev: Dict[str, Optional[str]] = {n: None for n in self._nodes}
        dist[src] = 0.0
        heap: List[Tuple[float, str]] = [(0.0, src)]
        visited: set = set()

        while heap:
            d, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            if u == dst:
                break
            for v, w in self._adj.get(u, {}).items():
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        if dist[dst] == float('inf'):
            return None

        path: List[str] = []
        cur: Optional[str] = dst
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def shortest_path_cost(self, src: str, dst: str) -> Optional[float]:
        """Total cost of the shortest path, or ``None`` if unreachable."""
        path = self.shortest_path(src, dst)
        if path is None:
            return None
        cost = 0.0
        for i in range(len(path) - 1):
            cost += self._adj[path[i]][path[i + 1]]
        return cost

    def word_path_info(self, word: str) -> Dict:
        """Classify each letter in *word* and check DCG-edge validity per step.

        Steps for non-alpha characters are skipped so the path covers only
        the meaningful symbolic content.
        """
        letters = [c for c in word if c.isalpha()]
        steps = []
        for i, ch in enumerate(letters):
            nd = self.node_data(ch)
            step: Dict = {
                'char':   ch,
                'class':  nd.get('class', '?'),
                'energy': round(nd.get('energy', 0.0), 6),
                'vector': [round(x, 6) for x in nd.get('vector', (0.0, 0.0, 0.0, 0.0))],
            }
            if i > 0:
                prev_ch = letters[i - 1]
                step['edge_from']    = prev_ch
                step['valid_step']   = self.has_edge(prev_ch, ch)
                step['edge_weight']  = self.edge_weight(prev_ch, ch)
            steps.append(step)

        all_valid = len(steps) <= 1 or all(s.get('valid_step', True) for s in steps)
        return {
            'word':          word,
            'steps':         steps,
            'total_energy':  round(word_sym_energy(word), 6),
            'vector_sum':    [round(x, 6) for x in word_vector(word)],
            'is_valid_path': all_valid,
        }


# ── Module-level lazy singleton ───────────────────────────────────────────────

_DCG_INSTANCE: Optional[DCG] = None


def get_dcg() -> DCG:
    """Return the shared DCG instance, building it on first call."""
    global _DCG_INSTANCE
    if _DCG_INSTANCE is None:
        _DCG_INSTANCE = _build_dcg()
    return _DCG_INSTANCE


def _build_dcg() -> DCG:
    """Construct the full 52-node DCG with all edge types."""
    g = DCG()

    upper_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]

    # 1. Uppercase ↔ lowercase  (DC ↔ AC form conversion)
    for u in upper_letters:
        lo = u.lower()
        g._add_edge(u,  lo, 1.0)   # DC → AC  (forward, cheaper)
        g._add_edge(lo, u,  2.0)   # AC → DC  (convergence, costlier)

    # 2. Within-class all-pairs  (same symmetry class, same case)
    for case_dict in (_CLASS_UPPER, _CLASS_LOWER):
        for letters in case_dict.values():
            for src in letters:
                for dst in letters:
                    if src != dst:
                        g._add_edge(src, dst, 1.0)

    # 3. Cross-class directed cycle  (energy-flow circuit)
    #    asym → biph → idemp → invol → asym  (same-case only)
    _cycle = [
        ('asymmetric',  'biphasic'),
        ('biphasic',    'idempotent'),
        ('idempotent',  'involutive'),
        ('involutive',  'asymmetric'),
    ]
    for case_dict in (_CLASS_UPPER, _CLASS_LOWER):
        for src_class, dst_class in _cycle:
            for src in case_dict[src_class]:
                for dst in case_dict[dst_class]:
                    g._add_edge(src, dst, 2.0)

    return g


# ── High-level helpers ────────────────────────────────────────────────────────

def homotopy_equivalent(
    word_a: str,
    word_b: str,
    tol: float = 1.0,
) -> Tuple[bool, Dict]:
    """Check homotopy equivalence of two words.

    Two words are homotopy-equivalent when their 4D vector sums are within
    *tol* (Euclidean distance) and their total SymPhi energies differ by at
    most *tol*.  This implements the path-homotopy criterion
    H(s,t) = (1−t)p₀(s) + t·p₁(s) from the whitepaper: if the interpolated
    path stays within the tolerance ball, the words are equivalent.
    """
    ea = word_sym_energy(word_a)
    eb = word_sym_energy(word_b)
    va = word_vector(word_a)
    vb = word_vector(word_b)

    e_diff = abs(ea - eb)
    v_dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(va, vb)))
    equiv  = e_diff <= tol and v_dist <= tol

    return equiv, {
        'word_a':          {'energy': round(ea, 6), 'vector': [round(x, 6) for x in va]},
        'word_b':          {'energy': round(eb, 6), 'vector': [round(x, 6) for x in vb]},
        'energy_diff':     round(e_diff, 6),
        'vector_distance': round(v_dist, 6),
        'tol':             tol,
        'equivalent':      equiv,
    }
