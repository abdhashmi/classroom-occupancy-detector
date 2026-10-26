from room_recommender import recommend_rooms


def run_tests():
    # Unknown occupancy rooms should remain eligible, with occupancy marked unknown.
    unknown_results = recommend_rooms(
        unavailable_room="VED226",
        required_capacity=35,
        required_type="classroom",
        current_time="09:00",
        observed_counts={},
    )
    unknown_rooms = {item["room"]: item for item in unknown_results}
    assert "VED329" in unknown_rooms
    assert unknown_rooms["VED329"]["occupancy_verified"] is False
    assert unknown_rooms["VED329"]["observed_count"] is None
    assert unknown_rooms["VED329"]["remaining_seats"] is None

    # Monitored room occupancy should be shown and spare capacity checked.
    occupied_results = recommend_rooms(
        unavailable_room="VED226",
        required_capacity=35,
        required_type="classroom",
        current_time="09:00",
        observed_counts={"VED329": 12},
    )
    occupied_rooms = {item["room"]: item for item in occupied_results}
    assert "VED329" in occupied_rooms
    assert occupied_rooms["VED329"]["occupancy_verified"] is True
    assert occupied_rooms["VED329"]["observed_count"] == 12
    assert occupied_rooms["VED329"]["remaining_seats"] == 58

    # A monitored room with insufficient spare seats should not be recommended.
    too_full_results = recommend_rooms(
        unavailable_room="VED226",
        required_capacity=35,
        required_type="classroom",
        current_time="09:00",
        observed_counts={"VED329": 40},
    )
    assert all(item["room"] != "VED329" for item in too_full_results)

    print("Occupancy recommendation tests passed.")


if __name__ == "__main__":
    run_tests()
