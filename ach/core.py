"""Analysis of Competing Hypotheses (ACH), scored the way Heuer describes it.

The hypothesis with the *least* evidence against it is preferred. Consistent
evidence doesn't add points, because a lot of evidence fits every hypothesis
and proves nothing. Each rating is weighted by how much the evidence can be
trusted, so a vendor's unverified claim counts for less than our own telemetry.

On top of the score, two checks:
  - diagnosticity: evidence rated the same for every hypothesis can't help
    choose between them, however important it looks;
  - linchpins: the smallest sets of evidence that, if they turned out to be
    wrong, would leave the leading hypothesis no longer ahead. That is what
    the conclusion actually rests on, and where collection should go next.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Rating codes. Only inconsistency is scored.
RATINGS = {
    "CC": 0,   # very consistent
    "C": 0,    # consistent
    "N": 0,    # neutral / not applicable
    "I": 1,    # inconsistent
    "II": 2,   # very inconsistent
    "?": 0,    # insufficient information: a collection gap, not evidence
}

# Weight by how far the evidence can be trusted (source reliability and
# information credibility combined, e.g. from Admiralty ratings).
CREDIBILITY = {"high": 1.0, "medium": 0.5, "low": 0.25, "none": 0.0}


@dataclass(frozen=True)
class Evidence:
    id: str
    text: str
    credibility: str
    ratings: dict
    note: str = ""

    def weight(self) -> float:
        return CREDIBILITY[self.credibility]

    def penalty(self, hypothesis: str) -> float:
        return RATINGS[self.ratings[hypothesis]] * self.weight()

    @property
    def unknown(self) -> bool:
        return all(r == "?" for r in self.ratings.values())


@dataclass
class Matrix:
    title: str
    hypotheses: dict
    evidence: list = field(default_factory=list)

    # -- loading ------------------------------------------------------------

    @classmethod
    def load(cls, path) -> "Matrix":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        hyps = data["hypotheses"]
        items = []
        seen = set()
        for raw in data["evidence"]:
            ev = Evidence(id=str(raw["id"]), text=raw["text"], credibility=raw["credibility"],
                          ratings={str(k): str(v) for k, v in raw["ratings"].items()},
                          note=raw.get("note", ""))
            if ev.id in seen:
                raise ValueError(f"duplicate evidence id {ev.id}")
            seen.add(ev.id)
            if ev.credibility not in CREDIBILITY:
                raise ValueError(f"{ev.id}: unknown credibility {ev.credibility!r}")
            if set(ev.ratings) != set(hyps):
                raise ValueError(f"{ev.id}: rate every hypothesis exactly once")
            bad = [r for r in ev.ratings.values() if r not in RATINGS]
            if bad:
                raise ValueError(f"{ev.id}: unknown rating {bad[0]!r}")
            items.append(ev)
        return cls(title=data.get("title", ""), hypotheses=hyps, evidence=items)

    # -- scoring ------------------------------------------------------------

    def scores(self, exclude=()) -> dict:
        """Weighted inconsistency per hypothesis. Lower is better."""
        return {h: round(sum(e.penalty(h) for e in self.evidence if e.id not in exclude), 4)
                for h in self.hypotheses}

    def inconsistent_count(self) -> dict:
        return {h: sum(1 for e in self.evidence if RATINGS[e.ratings[h]] > 0) for h in self.hypotheses}

    def ranking(self, exclude=()) -> list:
        s = self.scores(exclude)
        return sorted(self.hypotheses, key=lambda h: (s[h], h))

    def leader(self, exclude=()):
        """The hypothesis strictly ahead of all others, or None on a tie."""
        s = self.scores(exclude)
        best = min(s.values())
        top = [h for h, v in s.items() if v == best]
        return top[0] if len(top) == 1 else None

    # -- checks -------------------------------------------------------------

    def diagnostic(self, ev: Evidence) -> bool:
        return len({ev.penalty(h) for h in self.hypotheses}) > 1

    def non_diagnostic(self) -> list:
        return [e for e in self.evidence if not e.unknown and not self.diagnostic(e)]

    def linchpins(self, max_size: int = 4) -> tuple[int | None, list]:
        """Smallest sets of evidence whose removal leaves the leader no longer ahead.

        Only evidence that counts against at least one other hypothesis can
        matter, so the search is limited to those items.
        """
        lead = self.leader()
        if lead is None:
            return 0, [()]
        candidates = [e.id for e in self.evidence
                      if any(e.penalty(h) > 0 for h in self.hypotheses if h != lead)]
        for size in range(1, max_size + 1):
            found = [combo for combo in itertools.combinations(candidates, size)
                     if self.leader(exclude=set(combo)) != lead]
            if found:
                return size, found
        return None, []

    def collection_gaps(self) -> list:
        return [e for e in self.evidence if e.unknown]


def compare(old: Matrix, new: Matrix) -> list:
    """Rating changes between two versions of the same matrix."""
    before = {e.id: e for e in old.evidence}
    changes = []
    for e in new.evidence:
        prev = before.get(e.id)
        if prev is None:
            changes.append((e.id, "added", "", ""))
            continue
        for h in new.hypotheses:
            if prev.ratings.get(h) != e.ratings[h]:
                changes.append((e.id, h, prev.ratings.get(h), e.ratings[h]))
    return changes
