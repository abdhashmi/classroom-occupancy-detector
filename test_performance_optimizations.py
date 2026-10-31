from datetime import datetime

from occupancy_tracker import OccupancyTracker
from availability_service import search_availability
from classrooms import classrooms


def test_bulk_latest_observations_sqlite(tmp_path):
    tracker = OccupancyTracker(db_path=tmp_path / "occupancy.db")
    tracker.update("VED226", 12, datetime.now(), "test")
    tracker.update("VED202", 0, datetime.now(), "test")

    result = tracker.get_observations(["VED226", "VED202", "UNKNOWN"])

    assert set(result) == {"VED226", "VED202"}
    assert result["VED226"]["count"] == 12
    assert result["VED202"]["count"] == 0


def test_availability_uses_one_bulk_observation_fetch(monkeypatch):
    class BulkTracker:
        def __init__(self):
            self.bulk_calls = 0
            self.single_calls = 0

        def get_observations(self, rooms=None):
            self.bulk_calls += 1
            return {}

        def get_observation(self, room):
            self.single_calls += 1
            raise AssertionError("Per-room database lookup should not be used")

    tracker = BulkTracker()
    preferred = next(iter(classrooms))
    info = classrooms[preferred]

    search_availability(
        preferred_room=preferred,
        day="Monday",
        start_time="16:00",
        end_time="17:00",
        required_capacity=1,
        required_type=info["type"],
        tracker=tracker,
        now=datetime(2026, 10, 30, 16, 0),
    )

    assert tracker.bulk_calls == 1
    assert tracker.single_calls == 0
