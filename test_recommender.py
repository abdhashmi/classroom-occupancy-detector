
from room_recommender import recommend_rooms


def display_recommendations(title, rooms):
    print(f"\n{title}")
    print("-" * 60)

    if not rooms:
        print("No suitable alternative classroom found.")
        return

    for room in rooms:
        print(f"Room: {room['room']}")
        print(f"Capacity: {room['capacity']}")
        print(f"Type: {room['type']}")
        print(f"Distance: {room['distance_metres']} metres")
        print(f"Route: {room['route']}")
        print()


rooms = recommend_rooms(
    unavailable_room="VED226",
    required_capacity=35,
    required_type="classroom",
    current_time="10:30"
)

display_recommendations(
    "Test 1: Alternative classroom for 35 students",
    rooms
)

rooms = recommend_rooms(
    unavailable_room="VED226",
    required_capacity=50,
    required_type="laboratory",
    current_time="10:30"
)

display_recommendations(
    "Test 2: Laboratory for 50 students",
    rooms
)
