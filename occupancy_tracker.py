
from datetime import datetime


class OccupancyTracker:
    def __init__(self):
        self.observations = {}

    def update(self, room, count, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        self.observations[room] = {
            "count": count,
            "timestamp": timestamp
        }

    def get_count(self, room):
        observation = self.observations.get(room)

        if observation is None:
            return None

        return observation["count"]

    def is_recent(self, room, max_age_seconds=300):
        observation = self.observations.get(room)

        if observation is None:
            return False

        age = (
            datetime.now() - observation["timestamp"]
        ).total_seconds()

        return 0 <= age <= max_age_seconds

    def get_available_rooms(self, classrooms):
        available = []

        for room, info in classrooms.items():
            count = self.get_count(room)

            if (
                count is not None
                and self.is_recent(room)
                and count < info["capacity"]
            ):
                available.append(room)

        return available
