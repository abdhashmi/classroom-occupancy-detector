
from classrooms import classrooms


def walking_minutes(start_room, destination_room):
    """Estimate walking time using building and floor rules."""

    if start_room not in classrooms or destination_room not in classrooms:
        return None

    start = classrooms[start_room]
    end = classrooms[destination_room]

    floor_difference = abs(start["floor"] - end["floor"])

    if start["building"] == end["building"]:
        return floor_difference + 1

    # Inter-building transfer base time plus floor difference.
    return 3 + floor_difference


def shortest_route(start_room, destination_room):
    """Return a direct room-to-room route and its estimated walking time."""

    if start_room not in classrooms or destination_room not in classrooms:
        return None, None

    if start_room == destination_room:
        return [start_room], 0

    minutes = walking_minutes(start_room, destination_room)

    if minutes is None:
        return None, None

    return [start_room, destination_room], minutes
