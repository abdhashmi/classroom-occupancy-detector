# Classroom Agent update files

Copy these replacement files into your existing `C:\Users\motas\classroom-agent` folder:
- classrooms.py
- timetable.py
- campus_graph.py
- room_recommender.py
- app.py

Do not replace or delete `occupancy.db`, `occupancy_tracker.py`, or `history_dashboard.py`.

## Important data notes
- Room capacities and floor rules are based on information supplied by the project owner.
- Walking times are estimates from the requested rule: same building = floor difference + 1 minute; between buildings = 3 + floor difference.
- Timetable entries were transcribed from screenshots and should be checked against the original timetable before operational use. Expected attendance was not provided and is intentionally left unknown.
- Timetable screenshot entries with FE-3 and MIN are excluded; the 13:00-14:00 period is treated as break.
- Extra timetable locations VISH302, VISH401, and VISH402 were added as classrooms with capacity 80 based on the supplied rule that VISH rooms are classrooms. Verify those rooms' existence/floor assignments.
- If a room code appears in the timetable but isn't in classrooms.py (for example, Chanakya Lab 4D), it can be scheduled but will not be eligible for recommendations until added to the inventory.
- VED505 compartments are represented as VED505-A through VED505-E, each capacity 30.
