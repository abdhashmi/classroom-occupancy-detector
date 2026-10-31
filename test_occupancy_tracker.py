from datetime import datetime, timedelta
from pathlib import Path

from occupancy_tracker import OccupancyTracker


def test_sqlite_tracker_api_and_history(tmp_path):
    db_path = tmp_path / "occupancy.db"
    tracker = OccupancyTracker(db_path=db_path, database_url="")
    timestamp = datetime.now() - timedelta(seconds=2)
    tracker.update("VED226", 17, timestamp=timestamp, source="test")

    observation = tracker.get_observation("VED226")
    assert observation["count"] == 17
    assert observation["timestamp"] == timestamp
    assert observation["source"] == "test"
    assert tracker.get_count("VED226", max_age_seconds=10) == 17
    assert tracker.get_history("VED226", limit=5)[0]["count"] == 17
    assert tracker.observations["VED226"]["count"] == 17
    assert tracker.is_shared is False


def test_sqlite_data_survives_reopening(tmp_path):
    db_path = tmp_path / "occupancy.db"
    first = OccupancyTracker(db_path=db_path, database_url="")
    first.update("VED229", 0, source="test")
    second = OccupancyTracker(db_path=db_path, database_url="")
    assert second.get_observation("VED229")["count"] == 0
