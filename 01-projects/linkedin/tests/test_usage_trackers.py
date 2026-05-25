from datetime import datetime, timedelta, timezone
from pathlib import Path

from usage.atom_usage import AtomUsageTracker
from usage.connection_usage import ConnectionUsageTracker


def test_atom_cooldown_primary(project_root: Path):
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json", cooldown_days_primary=30)
    tracker.mark_used("sample-concept", role="primary", post_id="p1")
    assert tracker.is_in_cooldown("sample-concept", role="primary") is True
    assert tracker.is_in_cooldown("sample-concept", role="auxiliary") is False


def test_atom_cooldown_expires(project_root: Path):
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json", cooldown_days_primary=30)
    past = datetime.now(timezone.utc) - timedelta(days=31)
    tracker.mark_used("sample-concept", role="primary", post_id="p1", at=past)
    assert tracker.is_in_cooldown("sample-concept", role="primary") is False


def test_connection_cooldown(project_root: Path):
    tracker = ConnectionUsageTracker(project_root / "state" / "connection-usage.json", cooldown_days=60)
    tracker.mark_used("sample-concept", "another-concept", post_id="p1")
    assert tracker.is_in_cooldown("sample-concept", "another-concept") is True
    # order-independent
    assert tracker.is_in_cooldown("another-concept", "sample-concept") is True
