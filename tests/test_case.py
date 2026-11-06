"""The NorthStar matrices produce the results the report states."""
from pathlib import Path

import yaml

from ach import Matrix

CASE = Path(__file__).resolve().parents[1] / "case"


def test_first_version():
    m = Matrix.load(CASE / "matrix_v1.yaml")
    assert m.scores() == {"H1": 0, "H2": 2.5, "H3": 6.5}
    assert m.leader() == "H1"
    assert m.linchpins() == (3, [("E2", "E5", "E10")])


def test_rerated_version_rests_on_two_outside_claims():
    m = Matrix.load(CASE / "matrix_v2.yaml")
    assert m.scores() == {"H1": 0, "H2": 0.75, "H3": 6.5}
    assert m.leader() == "H1"
    size, sets = m.linchpins()
    assert size == 2 and sets == [("E10", "E12")]
    byid = {e.id: e for e in m.evidence}
    assert {byid[i].credibility for i in sets[0]} == {"medium", "low"}


def test_h3_unaffected_by_rerating():
    v1, v2 = Matrix.load(CASE / "matrix_v1.yaml"), Matrix.load(CASE / "matrix_v2.yaml")
    assert v1.scores()["H3"] == v2.scores()["H3"] == 6.5


def test_open_questions_are_listed():
    m = Matrix.load(CASE / "matrix_v2.yaml")
    assert [e.id for e in m.collection_gaps()] == ["E15", "E16", "E17", "E18"]


def test_generated_reports_are_current():
    from ach.__main__ import render
    v1, v2 = Matrix.load(CASE / "matrix_v1.yaml"), Matrix.load(CASE / "matrix_v2.yaml")
    assert (CASE / "ach_v1.md").read_text(encoding="utf-8") == render(v1)
    assert (CASE / "ach_v2.md").read_text(encoding="utf-8") == render(v2, v1)


def test_attack_mapping_shape():
    rows = yaml.safe_load((CASE / "attack_mapping.yaml").read_text())["mapping"]
    assert len(rows) == 13
    assert all(set(r) == {"observation", "tactic", "id", "name"} for r in rows)
    assert "T1070.001" not in {r["id"] for r in rows}          # revoked in v19
