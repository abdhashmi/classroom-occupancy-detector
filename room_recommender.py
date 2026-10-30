
from classrooms import classrooms
from timetable import get_schedule
from campus_graph import shortest_route


def recommend_rooms(
    unavailable_room,
    required_capacity,
    required_type,
    current_time,
    occupied_rooms=None,
    required_building=None,
    required_floor=None,
    require_accessibility=False,
    observed_counts=None,
):
    """Recommend rooms using occupancy, capacity, timetable, and walking time."""

    if (
        not isinstance(required_capacity, int)
        or isinstance(required_capacity, bool)
        or required_capacity < 1
    ):
        return []

    observed_counts = observed_counts or {}
    occupied_rooms = set(occupied_rooms or [])
    recommendations = []

    for room_id, info in classrooms.items():
        if room_id == unavailable_room or room_id in occupied_rooms:
            continue

        if info.get("capacity", 0) < required_capacity:
            continue

        if info.get("type") != required_type:
            continue

        if required_building and info.get("building") != required_building:
            continue

        if required_floor is not None and info.get("floor") != required_floor:
            continue

        if require_accessibility and not info.get("accessible", False):
            continue

        # Skip rooms that have a class at the selected time.
        if get_schedule(room_id, current_time) is not None:
            continue

        route, walking_minutes = shortest_route(unavailable_room, room_id)

        if route is None or walking_minutes is None:
            continue

        observed_count = observed_counts.get(room_id)
        is_verified = (
            isinstance(observed_count, int)
            and not isinstance(observed_count, bool)
            and observed_count >= 0
        )

        if is_verified:
            remaining_seats = max(0, info["capacity"] - observed_count)
            if remaining_seats < required_capacity:
                continue
        else:
            observed_count = None
            remaining_seats = None

        recommendations.append({
            "room": room_id,
            "building": info["building"],
            "floor": info["floor"],
            "capacity": info["capacity"],
            "type": info["type"],
            "walking_minutes": walking_minutes,
            # Temporary compatibility for existing tests or code.
            "distance_metres": walking_minutes,
            "route": " -> ".join(route),
            "observed_count": observed_count,
            "occupancy_verified": is_verified,
            "remaining_seats": remaining_seats,
        })

    recommendations.sort(
        key=lambda item: (
            not item["occupancy_verified"],
            item["walking_minutes"],
            item["capacity"],
        )
    )

    return recommendations
