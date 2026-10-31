# Classroom Agent performance fix

This patch addresses avoidable database latency after switching the app to Neon.

## Files to replace in the existing project

Copy these three files into the project root, replacing the existing files:

- `app.py`
- `occupancy_tracker.py`
- `availability_service.py`

Do not replace or delete `.streamlit/secrets.toml`, `occupancy.db`, or your SQLite backup files.

## Changes

1. `OccupancyTracker.get_observations()` retrieves the latest observation for all requested rooms in one query. The availability finder now uses this bulk method rather than opening a new Neon connection for every room.
2. `get_observation()` reuses the bulk method for single-room lookups.
3. Webcam observations are written at most once every five seconds per Streamlit session, rather than writing the same latest frame on every app rerun.

## Apply

1. Stop Streamlit with `Ctrl+C`.
2. Make a backup copy of the current `app.py`, `occupancy_tracker.py`, and `availability_service.py`.
3. Extract this ZIP and copy the three Python files into the project root.
4. Keep `.streamlit/secrets.toml` unchanged.
5. Run `python -m pytest -q` if the project test files are present.
6. Start with `streamlit run app.py`.

The patch does not change the Neon schema or modify occupancy records.


## Occupancy freshness window

The shared freshness setting is `OCCUPANCY_FRESHNESS_SECONDS = 15 * 60` (900 seconds). It is used by the occupancy tracker, availability search, app status display, and occupancy history dashboard. An observation remains stored in the database after it becomes stale; only its freshness classification changes.
