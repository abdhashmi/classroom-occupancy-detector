
import os
import tempfile
from datetime import datetime, timedelta

from occupancy_tracker import OccupancyTracker


def run_tests():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_occupancy.db")
        tracker = OccupancyTracker(db_path=db_path)

        try:
            # Test saving an observation.
            now = datetime.now()
            tracker.update("VED226", 12, timestamp=now)

            assert tracker.get_count("VED226") == 12
            assert tracker.is_recent("VED226") is True

            # Test saving another room.
            tracker.update("VED329", 0, timestamp=now)

            assert tracker.get_count("VED329") == 0
            assert tracker.is_recent("VED329") is True

            # Test that old observations are not recent.
            old_time = now - timedelta(minutes=10)
            tracker.update("VED505", 5, timestamp=old_time)

            assert tracker.is_recent("VED505") is False

        finally:
            # Close SQLite connections before the temporary
            # directory attempts to delete the database file.
            if hasattr(tracker, "close"):
                tracker.close()

    # Verify persistence after reopening the database.
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_occupancy.db")

        first_tracker = OccupancyTracker(db_path=db_path)
        first_tracker.update("VED226", 18)

        if hasattr(first_tracker, "close"):
            first_tracker.close()

        second_tracker = OccupancyTracker(db_path=db_path)
        try:
            assert second_tracker.get_count("VED226") == 18
        finally:
            if hasattr(second_tracker, "close"):
                second_tracker.close()

    print("SQLite persistence tests passed.")


if __name__ == "__main__":
    run_tests()
