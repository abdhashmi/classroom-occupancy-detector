from datetime import datetime
import os
import tempfile

from occupancy_tracker import OccupancyTracker


def run_tests():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "history_test.db")
        tracker = OccupancyTracker(db_path=db_path)
        try:
            tracker.update("VED226", 7, timestamp=datetime.now(), source="image_upload")
            tracker.update("VED226", 9, timestamp=datetime.now(), source="webcam")
            history = tracker.get_history("VED226", limit=10)
            assert len(history) == 2, f"Expected 2 records, got {len(history)}"
            assert history[0]["source"] == "webcam", history[0]
            assert history[0]["count"] == 9, history[0]
            assert tracker.get_observation("VED226")["count"] == 9
        finally:
            tracker.close()
    print("Occupancy history tests passed.")


if __name__ == "__main__":
    run_tests()
