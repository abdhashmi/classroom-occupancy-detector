
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
    require_accessibility=False
):
    occupied_rooms = set(occupied_rooms or [])
    recommendations = []

    for room_id, info in classrooms.items():
        if room_id == unavailable_room:
            continue

        if info["capacity"] < required_capacity:
            continue

        if info["type"] != required_type:
            continue

        if required_building and info["building"] != required_building:
            continue

        if required_floor is not None and info["floor"] != required_floor:
            continue

        if require_accessibility and not info.get("accessible", False):
            continue

        if room_id in occupied_rooms:
            continue

        schedule = get_schedule(room_id, current_time)

        if schedule is not None:
            continue

        route, distance = shortest_route(unavailable_room, room_id)

        if route is None:
            continue

        recommendations.append({
            "room": room_id,
            "building": info["building"],
            "floor": info["floor"],
            "capacity": info["capacity"],
            "type": info["type"],
            "distance_metres": distance,
            "route": " -> ".join(route)
        })

    recommendations.sort(
        key=lambda room: (
            room["distance_metres"],
            room["capacity"]
        )
    )

    return recommendations
