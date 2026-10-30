
from campus_graph import shortest_route, walking_minutes


def test_same_floor():
    assert walking_minutes("VED226", "VED202") == 1


def test_one_floor_apart():
    assert walking_minutes("VED226", "VED329") == 2


def test_three_floors_apart():
    assert walking_minutes("VED226", "VED505-E") == 4


def test_interbuilding_same_floor():
    assert walking_minutes("VED402", "VISH405") == 3


def test_interbuilding_floor_difference():
    assert walking_minutes("VED226", "VISH511") == 6


def test_route_returns_valid_compartment():
    route, minutes = shortest_route("VED226", "VED505-E")
    assert route == ["VED226", "VED505-E"]
    assert minutes == 4


def test_unknown_room_returns_none():
    assert walking_minutes("UNKNOWN", "VED226") is None
