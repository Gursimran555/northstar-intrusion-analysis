#!/usr/bin/env python3
"""Check an ATT&CK mapping file against an ATT&CK Enterprise STIX bundle.

    python tools/check_attack.py --attack enterprise-attack-20.0.json case/attack_mapping.yaml

For every row: the ID exists, isn't revoked or deprecated, the name matches,
and the tactic is one the technique belongs to. A revoked ID prints the ID that
replaced it (e.g. T1070.001 -> T1685.005 since ATT&CK v19).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def ext_id(obj):
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def load(bundle_path: Path):
    objs = json.loads(bundle_path.read_text(encoding="utf-8"))["objects"]
    by_stix = {o["id"]: o for o in objs}
    techniques, replaced_by = {}, {}
    for o in objs:
        if o["type"] == "attack-pattern":
            techniques.setdefault(ext_id(o), []).append(o)
    for r in objs:
        if r["type"] == "relationship" and r["relationship_type"] == "revoked-by":
            src, dst = by_stix.get(r["source_ref"]), by_stix.get(r["target_ref"])
            if src and dst and src["type"] == "attack-pattern":
                replaced_by[ext_id(src)] = ext_id(dst)
    return techniques, replaced_by


def check(rows, techniques, replaced_by) -> list[str]:
    problems = []
    for row in rows:
        tid = row["id"]
        live = [o for o in techniques.get(tid, []) if not o.get("revoked") and not o.get("x_mitre_deprecated")]
        if not live:
            hint = f" (replaced by {replaced_by[tid]})" if tid in replaced_by else ""
            problems.append(f"{tid}: not a current technique{hint}")
            continue
        t = live[0]
        if t["name"] != row["name"]:
            problems.append(f"{tid}: name is {t['name']!r}, mapping says {row['name']!r}")
        tactics = [k["phase_name"] for k in t.get("kill_chain_phases", [])]
        if row["tactic"] not in tactics:
            problems.append(f"{tid}: tactic {row['tactic']!r} not in {tactics}")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attack", required=True, type=Path)
    ap.add_argument("mapping", type=Path)
    args = ap.parse_args(argv)
    rows = yaml.safe_load(args.mapping.read_text(encoding="utf-8"))["mapping"]
    techniques, replaced_by = load(args.attack)
    problems = check(rows, techniques, replaced_by)
    for p in problems:
        print("FAIL", p)
    print(f"{len(rows) - len(problems)}/{len(rows)} mappings valid")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
