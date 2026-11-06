import textwrap

import pytest

from ach import Matrix, compare
from ach.__main__ import main


def write(tmp_path, body, name="m.yaml"):
    p = tmp_path / name
    p.write_text(textwrap.dedent(body))
    return p


BASIC = """
    title: t
    hypotheses: {A: a, B: b}
    evidence:
      - {id: E1, text: x, credibility: high, ratings: {A: C, B: I}}
      - {id: E2, text: y, credibility: medium, ratings: {A: C, B: I}}
      - {id: E3, text: z, credibility: high, ratings: {A: C, B: C}}
      - {id: E4, text: w, credibility: low, ratings: {A: II, B: N}}
      - {id: E5, text: gap, credibility: high, ratings: {A: "?", B: "?"}}
"""


def test_scores_count_only_inconsistency(tmp_path):
    m = Matrix.load(write(tmp_path, BASIC))
    assert m.scores() == {"A": 0.5, "B": 1.5}           # A: II*0.25 ; B: 1 + 0.5
    assert m.inconsistent_count() == {"A": 1, "B": 2}
    assert m.ranking() == ["A", "B"] and m.leader() == "A"


def test_non_diagnostic_and_gaps(tmp_path):
    m = Matrix.load(write(tmp_path, BASIC))
    assert [e.id for e in m.non_diagnostic()] == ["E3"]
    assert [e.id for e in m.collection_gaps()] == ["E5"]


def test_linchpin_is_smallest_set(tmp_path):
    m = Matrix.load(write(tmp_path, BASIC))
    size, sets = m.linchpins()
    # removing E1 leaves B at 0.5 = A's 0.5 -> tie, so A is no longer ahead
    assert size == 1 and sets == [("E1",)]


def test_tie_has_no_leader(tmp_path):
    m = Matrix.load(write(tmp_path, """
        hypotheses: {A: a, B: b}
        evidence:
          - {id: E1, text: x, credibility: high, ratings: {A: I, B: I}}
    """))
    assert m.leader() is None and m.linchpins() == (0, [()])


def test_zero_weight_evidence_never_matters(tmp_path):
    m = Matrix.load(write(tmp_path, """
        hypotheses: {A: a, B: b}
        evidence:
          - {id: E1, text: x, credibility: high, ratings: {A: C, B: I}}
          - {id: E2, text: rumour, credibility: none, ratings: {A: II, B: C}}
    """))
    assert m.scores() == {"A": 0.0, "B": 1.0}
    assert m.linchpins() == (1, [("E1",)])


@pytest.mark.parametrize("bad, msg", [
    ("{id: E1, text: x, credibility: sure, ratings: {A: C, B: C}}", "credibility"),
    ("{id: E1, text: x, credibility: high, ratings: {A: C}}", "every hypothesis"),
    ("{id: E1, text: x, credibility: high, ratings: {A: C, B: maybe}}", "rating"),
])
def test_validation(tmp_path, bad, msg):
    p = write(tmp_path, "hypotheses: {A: a, B: b}\nevidence:\n  - " + bad + "\n")
    with pytest.raises(ValueError, match=msg):
        Matrix.load(p)


def test_duplicate_ids_rejected(tmp_path):
    p = write(tmp_path, """
        hypotheses: {A: a}
        evidence:
          - {id: E1, text: x, credibility: high, ratings: {A: C}}
          - {id: E1, text: y, credibility: high, ratings: {A: C}}
    """)
    with pytest.raises(ValueError, match="duplicate"):
        Matrix.load(p)


def test_compare_and_cli(tmp_path, capsys):
    old = write(tmp_path, BASIC, "old.yaml")
    new = write(tmp_path, BASIC.replace("{A: C, B: I}}\n      - {id: E2", "{A: C, B: C}}\n      - {id: E2"), "new.yaml")
    assert compare(Matrix.load(old), Matrix.load(new)) == [("E1", "B", "I", "C")]
    out_md = tmp_path / "out.md"
    assert main([str(new), "--compare", str(old), "--markdown", str(out_md)]) == 0
    assert "E1 for B: I -> C" in out_md.read_text()
