
from collections import deque
from statistics import median


class ClassroomAgent:
    def __init__(self, room, capacity, window_size=3):
        self.room = room
        self.capacity = capacity
        self.window_size = window_size
        self.history = []
        self.recent_counts = deque(maxlen=window_size)
        self.current_period = None
        self.state = "UNKNOWN"

    def observe(
        self,
        count,
        scheduled,
        period=None,
        fresh=True
    ):
        if not fresh or count < 0:
            self.state = "UNKNOWN"
            return self.state

        if period != self.current_period:
            self.recent_counts.clear()
            self.current_period = period

        self.recent_counts.append(count)
        smoothed_count = median(self.recent_counts)

        if count > self.capacity:
            self.state = "OVER_CAPACITY"
        elif not scheduled and count > 0:
            self.state = "UNSCHEDULED_USAGE"
        elif not scheduled and count == 0:
            self.state = "EMPTY"
        elif smoothed_count > 0:
            self.state = "OCCUPIED"
        else:
            self.state = "EMPTY"

        self.history.append({
            "detected_count": count,
            "smoothed_count": smoothed_count,
            "scheduled": scheduled,
            "period": period,
            "state": self.state
        })

        return self.state

    def check_attendance(
        self,
        observed_count,
        expected_count,
        threshold=10
    ):
        difference = expected_count - observed_count

        if difference > threshold:
            return (
                f"LOW_ATTENDANCE: "
                f"{difference} fewer students detected"
            )

        if difference < -threshold:
            return (
                f"MORE_THAN_EXPECTED: "
                f"{abs(difference)} additional students detected"
            )

        return "ATTENDANCE_NORMAL"
