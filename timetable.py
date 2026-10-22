
from datetime import datetime

timetable = [
    {
        "room": "VED226",
        "start": "10:00",
        "end": "11:00",
        "expected_students": 35,
        "type": "classroom"
    },
    {
        "room": "VED329",
        "start": "11:00",
        "end": "12:00",
        "expected_students": 65,
        "type": "classroom"
    },
    {
        "room": "VED505",
        "start": "12:00",
        "end": "13:00",
        "expected_students": 25,
        "type": "laboratory"
    }
]


def get_schedule(room, current_time=None):
    if current_time is None:
        current_time = datetime.now().strftime("%H:%M")

    for entry in timetable:
        if (
            entry["room"] == room
            and entry["start"] <= current_time < entry["end"]
        ):
            return entry

    return None
