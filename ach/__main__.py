"""python -m ach MATRIX.yaml [--compare OLD.yaml] [--markdown OUT.md]"""

from __future__ import annotations

import argparse
import sys

from .core import Matrix, compare


def render(m: Matrix, old: Matrix | None = None) -> str:
    out = [f"# {m.title}", ""]
    scores, counts = m.scores(), m.inconsistent_count()
    out += ["## Ranking", "",
            "Weighted inconsistency (lower is better). Consistent evidence doesn't score.", "",
            "| Hypothesis | Weighted score | Items against |", "|---|---|---|"]
    for h in m.ranking():
        out.append(f"| {h}: {m.hypotheses[h]} | {scores[h]:g} | {counts[h]} |")

    lead = m.leader()
    size, sets = m.linchpins()
    out += ["", "## What the leading hypothesis rests on", ""]
    if lead is None:
        out.append("No hypothesis is ahead: the top scores are tied.")
    elif size is None:
        out.append(f"{lead} stays ahead even if any 4 pieces of evidence are removed.")
    else:
        out.append(f"{lead} stops being ahead if these {size} item(s) are wrong or removed:")
        out.append("")
        byid = {e.id: e for e in m.evidence}
        for combo in sets:
            out.append("- " + " + ".join(f"{i} ({byid[i].credibility} credibility): {byid[i].text}"
                                         for i in combo))

    nd = m.non_diagnostic()
    out += ["", "## Evidence that doesn't separate the hypotheses", ""]
    out += [f"- {e.id}: {e.text}" for e in nd] or ["- none"]

    gaps = m.collection_gaps()
    out += ["", "## Unrated (needs collection)", ""]
    out += [f"- {e.id}: {e.text}" + (f" ({e.note})" if e.note else "") for e in gaps] or ["- none"]

    if old is not None:
        changes = compare(old, m)
        out += ["", "## Changes from the previous version", "",
                f"Previous scores: " + ", ".join(f"{h} {v:g}" for h, v in old.scores().items()), ""]
        byid = {e.id: e for e in m.evidence}
        for eid, h, before, after in changes:
            if h == "added":
                out.append(f"- {eid} added: {byid[eid].text}")
            else:
                note = f" ({byid[eid].note})" if byid[eid].note else ""
                out.append(f"- {eid} for {h}: {before} -> {after}{note}")

    out += ["", "## Matrix", "", "| # | Evidence | Credibility | " +
            " | ".join(m.hypotheses) + " |", "|---|---|---|" + "---|" * len(m.hypotheses)]
    for e in m.evidence:
        out.append(f"| {e.id} | {e.text} | {e.credibility} | " +
                   " | ".join(e.ratings[h] for h in m.hypotheses) + " |")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ach")
    ap.add_argument("matrix")
    ap.add_argument("--compare")
    ap.add_argument("--markdown")
    args = ap.parse_args(argv)
    m = Matrix.load(args.matrix)
    old = Matrix.load(args.compare) if args.compare else None
    text = render(m, old)
    if args.markdown:
        with open(args.markdown, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
