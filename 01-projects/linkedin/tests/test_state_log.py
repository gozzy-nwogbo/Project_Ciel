import json
from pathlib import Path

from state_log import StateLog


def test_appends_jsonl(project_root: Path):
    log = StateLog(project_root / "logs" / "state.jsonl")
    log.record(slug="x", from_status="drafting", to_status="text_ready", actor="engine")
    log.record(slug="x", from_status="text_ready", to_status="gate1_approved", actor="user")
    lines = (project_root / "logs" / "state.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["slug"] == "x"
    assert first["to_status"] == "text_ready"
    assert "timestamp" in first
