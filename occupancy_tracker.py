
from contextlib import contextmanager
from datetime import datetime
import sqlite3
from pathlib import Path


def _now_local_naive():
    return datetime.now()


class OccupancyTracker:
    """SQLite-backed occupancy history with properly closed connections."""

    def __init__(self, db_path="occupancy.db"):
        self.db_path = str(db_path)
        self._initialize_database()

    @contextmanager
    def _connect(self):
        """Open a connection and always close it after use."""
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row

        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def close(self):
        """Compatibility method; connections are closed after each operation."""
        pass

    def _initialize_database(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS occupancy_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room TEXT NOT NULL,
                    count INTEGER NOT NULL CHECK (count >= 0),
                    observed_at TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'unknown'
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_occupancy_room_time
                ON occupancy_observations(room, observed_at DESC)
            """)

    @property
    def observations(self):
        """Return the latest observation for each room."""
        with self._connect() as connection:
            rows = connection.execute("""
                SELECT o.room, o.count, o.observed_at
                FROM occupancy_observations o
                JOIN (
                    SELECT room, MAX(id) AS latest_id
                    FROM occupancy_observations
                    GROUP BY room
                ) latest ON latest.latest_id = o.id
            """).fetchall()

        result = {}
        for row in rows:
            try:
                timestamp = datetime.fromisoformat(row["observed_at"])
            except (TypeError, ValueError):
                continue

            result[row["room"]] = {
                "count": int(row["count"]),
                "timestamp": timestamp,
            }

        return result

    def update(self, room, count, timestamp=None, source="unknown"):
        if not isinstance(room, str) or not room.strip():
            raise ValueError("room must be a non-empty string")

        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError("count must be a non-negative integer")

        if timestamp is None:
            timestamp = _now_local_naive()

        if not isinstance(timestamp, datetime):
            raise TypeError("timestamp must be a datetime")

        if not isinstance(source, str) or not source.strip():
            source = "unknown"

        with self._connect() as connection:
            connection.execute("""
                INSERT INTO occupancy_observations
                    (room, count, observed_at, source)
                VALUES (?, ?, ?, ?)
            """, (
                room.strip(),
                count,
                timestamp.isoformat(),
                source.strip(),
            ))

    def get_observation(self, room):
        with self._connect() as connection:
            row = connection.execute("""
                SELECT room, count, observed_at, source
                FROM occupancy_observations
                WHERE room = ?
                ORDER BY id DESC
                LIMIT 1
            """, (room,)).fetchone()

        if row is None:
            return None

        try:
            timestamp = datetime.fromisoformat(row["observed_at"])
        except (TypeError, ValueError):
            return None

        return {
            "count": int(row["count"]),
            "timestamp": timestamp,
            "source": row["source"],
        }

    def get_history(self, room=None, limit=100):
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")

        with self._connect() as connection:
            if room is None:
                rows = connection.execute("""
                    SELECT id, room, count, observed_at, source
                    FROM occupancy_observations
                    ORDER BY id DESC LIMIT ?
                """, (limit,)).fetchall()
            else:
                rows = connection.execute("""
                    SELECT id, room, count, observed_at, source
                    FROM occupancy_observations
                    WHERE room = ?
                    ORDER BY id DESC LIMIT ?
                """, (room, limit)).fetchall()

        history = []
        for row in rows:
            try:
                timestamp = datetime.fromisoformat(row["observed_at"])
            except (TypeError, ValueError):
                continue

            history.append({
                "id": row["id"],
                "room": row["room"],
                "count": int(row["count"]),
                "timestamp": timestamp,
                "source": row["source"],
            })

        return history

    def age_seconds(self, room, now=None):
        observation = self.get_observation(room)
        if observation is None:
            return None

        now = now or _now_local_naive()

        try:
            return (now - observation["timestamp"]).total_seconds()
        except TypeError:
            return None

    def is_recent(self, room, max_age_seconds=300, now=None):
        if max_age_seconds < 0:
            return False

        age = self.age_seconds(room, now)
        return age is not None and 0 <= age <= max_age_seconds

    def get_count(self, room, max_age_seconds=300, now=None):
        observation = self.get_observation(room)

        if observation is None:
            return None

        if not self.is_recent(room, max_age_seconds, now):
            return None

        return observation["count"]

    def get_available_rooms(self, classrooms, max_age_seconds=300, now=None):
        available = []

        for room, info in classrooms.items():
            count = self.get_count(
                room,
                max_age_seconds=max_age_seconds,
                now=now,
            )

            if count == 0 and info.get("capacity", 0) > 0:
                available.append(room)

        return available
