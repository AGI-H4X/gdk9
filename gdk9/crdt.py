from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class LwwEntry:
  value: Any
  timestamp: float
  actor: str


def coerce_entry(raw: Any, default_actor: str = "legacy", default_ts: float = 0.0) -> LwwEntry:
  if isinstance(raw, dict) and {"value", "timestamp", "actor"} <= set(raw.keys()):
    return LwwEntry(raw.get("value"), float(raw.get("timestamp", default_ts)), str(raw.get("actor", default_actor)))
  return LwwEntry(raw, float(default_ts), default_actor)


def lww_merge(a: LwwEntry, b: LwwEntry) -> LwwEntry:
  if b.timestamp > a.timestamp:
    return b
  if b.timestamp < a.timestamp:
    return a
  return b if b.actor >= a.actor else a


def stamp(value: Any, actor: str | None = None, ts: float | None = None) -> Dict[str, Any]:
  return {
    "value": value,
    "timestamp": float(time.time() if ts is None else ts),
    "actor": actor or "anonymous",
  }


def merge_maps(
  left: Dict[str, Any],
  right: Dict[str, Any],
  default_actor: str = "legacy",
  default_ts: float = 0.0,
) -> Tuple[Dict[str, Any], Dict[str, int], Dict[str, str]]:
  merged: Dict[str, Any] = {}
  stats = {"added": 0, "updated": 0, "unchanged": 0}
  winners: Dict[str, str] = {}
  keys = set(left.keys()) | set(right.keys())
  for key in keys:
    lentry = coerce_entry(left.get(key), default_actor, default_ts)
    rentry = coerce_entry(right.get(key), default_actor, default_ts)
    winner = lww_merge(lentry, rentry)
    merged[key] = {"value": winner.value, "timestamp": winner.timestamp, "actor": winner.actor}
    if winner is lentry:
      winners[key] = "left"
    else:
      winners[key] = "right"
    if key not in left:
      stats["added"] += 1
    elif winner.value != lentry.value or winner.timestamp != lentry.timestamp or winner.actor != lentry.actor:
      stats["updated"] += 1
    else:
      stats["unchanged"] += 1
  return merged, stats, winners
