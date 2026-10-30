from datetime import datetime, timedelta

import pytest

from availability_service import classes_overlapping, normalize_day, search_availability
from occupancy_tracker import OccupancyTracker


class FakeTracker:
    def __init__(self, observations=None):
        self.observations = observations or {}

    def get_observation(self, room):
        return self.observations.get(room)


def test_day_aliases():
    assert normalize_day("Tu") == "Tuesday"
    assert normalize_day("friday") == "Friday"


def test_class_overlap_is_for_full_interval():
    rows = classes_overlapping("Tuesday", "16:00", "17:00")
    assert any(row["section"] == "S" and row["room"] == "VED226" for row in rows)
    assert any(row["section"] == "R" and row["room"] == "VED227" for row in rows)
    assert not any(row["room"] == "VED226" for row in classes_overlapping("Tuesday", "17:00", "18:00"))


def test_classes_from_all_sections_are_returned():
    rows = classes_overlapping("Monday", "09:00", "10:00")
    assert {row["section"] for row in rows} >= {"S", "T"}


def test_recent_empty_is_confirmed_available():
    now = datetime(2026, 10, 29, 12, 0)
    tracker = FakeTracker({
        "VED202": {"count": 0, "timestamp": now - timedelta(seconds=30), "source": "webcam"}
    })
    result = search_availability("VED226", "Tuesday", "16:00", "17:00", 35, "classroom", tracker, now=now)
    item = next(row for row in result["available"] if row["room"] == "VED202")
    assert item["status"] == "RECENTLY OBSERVED EMPTY"


def test_missing_observation_is_unverified_not_available():
    now = datetime(2026, 10, 29, 12, 0)
    result = search_availability("VED226", "Tuesday", "16:00", "17:00", 35, "classroom", FakeTracker(), now=now)
    assert any(row["room"] == "VED202" for row in result["unverified"])
    assert not any(row["room"] == "VED202" for row in result["available"])


def test_stale_observation_is_unverified():
    now = datetime(2026, 10, 29, 12, 0)
    tracker = FakeTracker({
        "VED202": {"count": 0, "timestamp": now - timedelta(seconds=301), "source": "webcam"}
    })
    result = search_availability("VED226", "Tuesday", "16:00", "17:00", 35, "classroom", tracker, now=now)
    assert any(row["room"] == "VED202" for row in result["unverified"])


def test_recent_occupied_is_not_marked_available():
    now = datetime(2026, 10, 29, 12, 0)
    tracker = FakeTracker({
        "VED202": {"count": 4, "timestamp": now - timedelta(seconds=30), "source": "webcam"}
    })
    result = search_availability("VED226", "Tuesday", "16:00", "17:00", 35, "classroom", tracker, now=now)
    assert any(row["room"] == "VED202" for row in result["occupied"])
    assert not any(row["room"] == "VED202" for row in result["available"])


def test_scheduled_room_excluded_and_section_details_preserved():
    now = datetime(2026, 10, 29, 12, 0)
    result = search_availability("VED202", "Tuesday", "16:00", "17:00", 35, "classroom", FakeTracker(), now=now)
    assert "VED227" in {row["room"] for row in result["classes_by_room"].get("VED227", [])}
    assert "VED227" not in {row["room"] for row in result["unverified"]}
    assert "VED227" not in {row["room"] for row in result["available"]}


def test_invalid_interval_raises():
    with pytest.raises(ValueError):
        classes_overlapping("Tuesday", "17:00", "16:00")
