# SQLite persistence milestone

This milestone replaces the in-memory occupancy tracker with SQLite persistence.
It is designed to work with the current app's existing `OccupancyTracker` API.

## Files to copy

Copy `occupancy_tracker.py` and `test_sqlite_tracker.py` into:
`C:\Users\motas\classroom-agent`

Replace the existing `occupancy_tracker.py`. Keep the rest of your project files.

## Test before starting the app

In VS Code terminal (from the project folder):

```powershell
python -m py_compile occupancy_tracker.py
python test_sqlite_tracker.py
```

Expected output:
`SQLite persistence tests passed.`

Then restart Streamlit. Press `Ctrl+C` in the terminal running Streamlit, then:

```powershell
streamlit run app.py
```

## What changes

- A file named `occupancy.db` is created in the project folder when the tracker starts.
- Each observation is stored in `occupancy_observations` with room, count, timestamp and source.
- The latest observation for each room remains available through `tracker.observations`, so the current dashboard can keep using it.
- Historical observations can be queried with `tracker.get_history(room=None, limit=100)`.
- Data survives Streamlit reruns and application restarts.

## Important

- Keep `occupancy.db` out of Git if it contains real occupancy records. Add `occupancy.db`, `occupancy.db-shm`, and `occupancy.db-wal` to `.gitignore`.
- This is a local SQLite database. It does not yet synchronize records between different laptops or a hosted application. A centralized database is a later deployment step.
- Webcam frames may generate many observations. If the history grows too quickly, we should add a sampling interval (for example, save at most one observation every 5 seconds per room) in a later refinement.
- Use Python from your `.venv`. If activation is unavailable, use `.\.venv\Scripts\python.exe` in place of `python`.
