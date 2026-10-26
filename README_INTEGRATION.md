# Occupancy recommendation update

This update changes recommendations as requested:

- Rooms without a fresh occupancy observation are not automatically excluded.
  They can be listed as **UNVERIFIED**, with occupied seats and remaining seats
  shown as **Unknown**.
- Monitored rooms display detected occupied seats and remaining seats.
- A monitored room is only recommended if it has enough remaining seats for the
  requested group.
- Rooms booked in the timetable at the selected evaluation time remain excluded.
- Rooms still need the requested type/capacity and a route in the campus graph.

## Install

Copy `app.py`, `room_recommender.py`, and `test_reliable_occupancy.py` into the
project folder, replacing the matching files. Keep `classrooms.py`,
`timetable.py`, `campus_graph.py`, `agent.py`, `occupancy_tracker.py`, and
`yolo26n.pt`.

From the project folder in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m py_compile app.py room_recommender.py
python test_reliable_occupancy.py
streamlit run app.py
```

A room marked **UNVERIFIED** is not guaranteed to be empty. Check the room before
sending people there. Observations remain in-memory until the SQLite milestone.
