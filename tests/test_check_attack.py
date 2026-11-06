import json

from tools.check_attack import check, load


def bundle(tmp_path):
    objs = [
        {"type": "attack-pattern", "id": "attack-pattern--new", "name": "Clear Windows Event Logs",
         "external_references": [{"source_name": "mitre-attack", "external_id": "T1685.005"}],
         "kill_chain_phases": [{"phase_name": "defense-impairment"}]},
        {"type": "attack-pattern", "id": "attack-pattern--old", "name": "Clear Windows Event Logs", "revoked": True,
         "external_references": [{"source_name": "mitre-attack", "external_id": "T1070.001"}]},
        {"type": "relationship", "id": "relationship--1", "relationship_type": "revoked-by",
         "source_ref": "attack-pattern--old", "target_ref": "attack-pattern--new"},
    ]
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"objects": objs}))
    return load(p)


def test_current_mapping_passes(tmp_path):
    t, r = bundle(tmp_path)
    assert check([{"id": "T1685.005", "name": "Clear Windows Event Logs", "tactic": "defense-impairment"}], t, r) == []


def test_revoked_id_points_to_replacement(tmp_path):
    t, r = bundle(tmp_path)
    out = check([{"id": "T1070.001", "name": "Clear Windows Event Logs", "tactic": "stealth"}], t, r)
    assert out == ["T1070.001: not a current technique (replaced by T1685.005)"]


def test_wrong_tactic_and_name(tmp_path):
    t, r = bundle(tmp_path)
    out = check([{"id": "T1685.005", "name": "Clear Logs", "tactic": "stealth"}], t, r)
    assert len(out) == 2
