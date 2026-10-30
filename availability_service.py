"""Timetable-aware classroom availability search.

A room is confirmed as recently observed empty only when it has no timetable
conflict and its latest occupancy observation is recent and has count == 0.
Missing or stale observations are returned separately as unverified.
"""
from datetime import datetime, time

from campus_graph import shortest_route
from classrooms import classrooms
from timetable import DAY_NAMES, timetable


DAY_ALIASES = {
    "monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday",
    "thursday": "Thursday", "friday": "Friday",
    "mo": "Monday", "tu": "Tuesday", "we": "Wednesday",
    "th": "Thursday", "fr": "Friday",
}


def normalize_day(day):
    if not isinstance(day, str):
        raise ValueError("day must be a weekday name or code")
    normalized = DAY_ALIASES.get(day.strip().lower())
    if normalized is None:
        raise ValueError(f"Unsupported weekday: {day!r}. Use Monday-Friday.")
    return normalized


def _parse_time(value, field_name):
    if isinstance(value, time):
        return value
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a time like '16:00'")
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise ValueError(f"{field_name} must use HH:MM format") from exc


def _time_text(value):
    return _parse_time(value, "time").strftime("%H:%M")


def classes_overlapping(day, start_time, end_time):
    """Return all S/R/T timetable entries overlapping the requested interval."""
    day_name = normalize_day(day)
    start = _parse_time(start_time, "start_time")
    end = _parse_time(end_time, "end_time")
    if end <= start:
        raise ValueError("end_time must be later than start_time")

    start_text, end_text = start.strftime("%H:%M"), end.strftime("%H:%M")
    rows = []
    for entry in timetable:
        if entry["day"] != day_name:
            continue
        # Half-open intervals: a class ending at 10:00 does not conflict
        # with a search starting at 10:00.
        if entry["start"] < end_text and entry["end"] > start_text:
            rows.append(dict(entry))
    return sorted(rows, key=lambda row: (row["start"], row["room"], row["section"]))


def search_availability(
    preferred_room,
    day,
    start_time,
    end_time,
    required_capacity,
    required_type,
    tracker,
    now=None,
    max_age_seconds=300,
):
    """Return schedule conflicts, section-wise classes, and ranked alternatives.

    The tracker is expected to implement get_observation(room). Observations
    must be recent and have count == 0 for a room to be in `available`.
    Missing/stale observations go to `unverified`, never `available`.
    """
    if preferred_room not in classrooms:
        raise ValueError(f"Unknown preferred room: {preferred_room}")
    if not isinstance(required_capacity, int) or isinstance(required_capacity, bool) or required_capacity < 1:
        raise ValueError("required_capacity must be a positive integer")
    if required_type not in {"classroom", "laboratory"}:
        raise ValueError("required_type must be 'classroom' or 'laboratory'")
    if not isinstance(max_age_seconds, (int, float)) or max_age_seconds < 0:
        raise ValueError("max_age_seconds must be non-negative")

    day_name = normalize_day(day)
    start = _parse_time(start_time, "start_time")
    end = _parse_time(end_time, "end_time")
    if end <= start:
        raise ValueError("end_time must be later than start_time")
    start_text, end_text = start.strftime("%H:%M"), end.strftime("%H:%M")
    now = now or datetime.now()

    scheduled_classes = classes_overlapping(day_name, start_text, end_text)
    classes_by_room = {}
    for entry in scheduled_classes:
        classes_by_room.setdefault(entry["room"], []).append(entry)

    preferred_conflicts = classes_by_room.get(preferred_room, [])
    available, unverified = [], []
    occupied = []
    excluded = []

    for room_id, info in classrooms.items():
        if room_id == preferred_room:
            continue
        if info.get("capacity", 0) < required_capacity:
            continue
        if info.get("type") != required_type:
            continue

        conflicts = classes_by_room.get(room_id, [])
        if conflicts:
            excluded.append({
                "room": room_id,
                "reason": "TIMETABLE CONFLICT",
                "classes": conflicts,
            })
            continue

        route, minutes = shortest_route(preferred_room, room_id)
        if route is None or minutes is None:
            continue

        observation = tracker.get_observation(room_id)
        age_seconds = None
        fresh = False
        count = None
        observed_at = None
        source = None
        if observation is not None:
            observed_at = observation.get("timestamp")
            count = observation.get("count")
            source = observation.get("source")
            if isinstance(observed_at, datetime):
                try:
                    age_seconds = (now - observed_at).total_seconds()
                    fresh = 0 <= age_seconds <= max_age_seconds
                except TypeError:
                    fresh = False

        item = {
            "room": room_id,
            "building": info["building"],
            "floor": info["floor"],
            "capacity": info["capacity"],
            "type": info["type"],
            "walking_minutes": minutes,
            "route": " -> ".join(route),
            "observed_count": count if fresh else None,
            "observation_age_seconds": age_seconds if fresh else None,
            "observed_at": observed_at if fresh else None,
            "observation_source": source if fresh else None,
            "remaining_seats": max(0, info["capacity"] - count) if fresh and isinstance(count, int) else None,
            "status": None,
        }

        if not fresh or not isinstance(count, int) or isinstance(count, bool) or count < 0:
            item["status"] = "UNVERIFIED"
            unverified.append(item)
        elif count == 0:
            item["status"] = "RECENTLY OBSERVED EMPTY"
            available.append(item)
        else:
            item["status"] = "RECENTLY OBSERVED OCCUPIED"
            occupied.append(item)

    sort_key = lambda item: (item["walking_minutes"], item["capacity"], item["room"])
    available.sort(key=sort_key)
    unverified.sort(key=sort_key)
    occupied.sort(key=sort_key)
    excluded.sort(key=lambda item: item["room"])

    return {
        "day": day_name,
        "start_time": start_text,
        "end_time": end_text,
        "preferred_room": preferred_room,
        "preferred_room_classes": preferred_conflicts,
        "preferred_room_has_timetable_conflict": bool(preferred_conflicts),
        "scheduled_classes": scheduled_classes,
        "classes_by_room": classes_by_room,
        "available": available,
        "unverified": unverified,
        "occupied": occupied,
        "excluded_by_timetable": excluded,
    }
