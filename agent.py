from collections import deque
from statistics import median


class ClassroomAgent:
    """Classify a room using a fresh person count and timetable status."""

    def __init__(self, room, capacity, window_size=3):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if window_size < 1:
            raise ValueError("window_size must be at least 1")

        self.room = room
        self.capacity = capacity
        self.window_size = window_size
        self.recent_counts = deque(maxlen=window_size)
        self.current_period = None
        self.history = []
        self.state = "UNKNOWN"

    def observe(self, count, scheduled, period=None, fresh=True):
        """Return a room state; stale or invalid observations are UNKNOWN."""
        if (
            not fresh
            or not isinstance(count, int)
            or isinstance(count, bool)
            or count < 0
        ):
            self.state = "UNKNOWN"
            return self.state

        if period != self.current_period:
            self.recent_counts.clear()
            self.current_period = period

        self.recent_counts.append(count)
        smoothed_count = median(self.recent_counts)

        # Current count is used for immediate safety checks. The median is
        # retained in history to help smooth trends without hiding crowding.
        if count > self.capacity:
            state = "OVER_CAPACITY"
        elif count > 0 and not scheduled:
            state = "UNSCHEDULED_USAGE"
        elif count > 0:
            state = "OCCUPIED"
        elif scheduled:
            state = "SCHEDULED_EMPTY"
        else:
            state = "AVAILABLE"

        self.state = state
        self.history.append({
            "detected_count": count,
            "smoothed_count": smoothed_count,
            "scheduled": bool(scheduled),
            "period": period,
            "state": state,
        })
        return state

    def check_attendance(self, observed_count, expected_count, threshold=10):
        if (
            not isinstance(observed_count, int)
            or isinstance(observed_count, bool)
            or not isinstance(expected_count, int)
            or isinstance(expected_count, bool)
            or observed_count < 0
            or expected_count < 0
            or threshold < 0
        ):
            return "INVALID_COUNTS"

        difference = expected_count - observed_count
        if difference > threshold:
            return f"LOW_ATTENDANCE: {difference} fewer students detected"
        if difference < -threshold:
            return (
                f"MORE_THAN_EXPECTED: {abs(difference)} "
                "additional students detected"
            )
        return "ATTENDANCE_NORMAL"
