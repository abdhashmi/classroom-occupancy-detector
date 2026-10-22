
from agent import ClassroomAgent
from classrooms import classrooms
from timetable import get_schedule

test_observations = {
    "VED226": [
        (10, "10:15"),
        (30, "10:20"),
        (32, "10:25"),
        (31, "10:30"),
        (15, "14:00")
    ],
    "VED329": [
        (65, "11:15"),
        (75, "11:20")
    ],
    "VED505": [
        (20, "12:15"),
        (0, "14:00")
    ]
}

for room, observations in test_observations.items():
    agent = ClassroomAgent(
        room,
        classrooms[room]["capacity"]
    )

    print("\n" + "=" * 60)
    print(f"CLASSROOM: {room}")
    print(f"Building: {classrooms[room]['building']}")
    print(f"Floor: {classrooms[room]['floor']}")
    print(f"Capacity: {classrooms[room]['capacity']}")
    print("=" * 60)

    for count, time in observations:
        schedule = get_schedule(room, time)
        scheduled = schedule is not None

        period = (
            (schedule["start"], schedule["end"])
            if schedule else time
        )

        state = agent.observe(
            count,
            scheduled,
            period=period
        )

        latest = agent.history[-1]

        expected = (
            schedule["expected_students"]
            if schedule else None
        )

        if schedule:
            attendance_status = agent.check_attendance(
                count,
                expected
            )
        else:
            attendance_status = "NO_CLASS_SCHEDULED"

        print(
            f"\nTime: {time}"
            f"\nDetected students: {count}"
            f"\nSmoothed occupancy: {latest['smoothed_count']}"
            f"\nScheduled: {scheduled}"
            f"\nExpected students: "
            f"{expected if expected is not None else 'N/A'}"
            f"\nClassroom state: {state}"
            f"\nAttendance check: {attendance_status}"
        )

    print(f"\nObservations stored: {len(agent.history)}")
