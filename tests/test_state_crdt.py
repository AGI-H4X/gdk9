from gdk9.state import merge_state, set_rule, set_symbol


def _mk_state(symbols=None, rules=None):
  return {"symbols": symbols or {}, "rules": rules or {}, "crdt": {"symbols": {}, "rules": {}}}


def test_merge_state_prefers_newer_symbols():
  left = _mk_state()
  right = _mk_state()
  set_symbol(left, "A", 1.0, actor="left", timestamp=1.0)
  set_symbol(right, "A", 2.0, actor="right", timestamp=2.0)
  set_symbol(right, "B", 3.0, actor="right", timestamp=2.0)

  merged, stats = merge_state(left, right)

  assert merged["symbols"]["A"] == 2.0
  assert merged["symbols"]["B"] == 3.0
  assert merged["crdt"]["symbols"]["A"]["actor"] == "right"
  assert stats["symbols"]["updated"] == 1
  assert stats["symbols"]["added"] == 1


def test_merge_state_handles_legacy_rules():
  legacy = {"symbols": {"X": 9.0}, "rules": {"R1": {"name": "R1", "type": "fusion", "arity": 2, "params": {"out": "Z"}}}}
  incoming = _mk_state()
  set_rule(incoming, "R1", {"name": "R1", "type": "fusion", "arity": 3, "params": {"out": "Z"}}, actor="peer", timestamp=5.0)

  merged, stats = merge_state(legacy, incoming)

  assert merged["rules"]["R1"]["arity"] == 3
  assert merged["crdt"]["rules"]["R1"]["actor"] == "peer"
  assert stats["rules"]["updated"] == 1
