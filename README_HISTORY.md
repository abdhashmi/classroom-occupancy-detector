# Occupancy History Dashboard integration

This milestone adds a history dashboard without replacing your working `app.py`.

## 1. Copy the module

Copy `history_dashboard.py` into your project folder:

`C:\Users\motas\classroom-agent`

## 2. Add the import to `app.py`

Near the other imports at the top, add:

```python
from history_dashboard import render_occupancy_history
```

## 3. Add the dashboard call

At the very bottom of `app.py`, after the existing Alternative Classroom Recommendations section and all its code, add:

```python
render_occupancy_history(tracker, classrooms)
```

Keep the line at the left edge (no indentation). It must be outside any `if`, `with`, or button block so the history section appears on every page rerun.

## 4. Record observation sources

In `app.py`, find the image upload tracker update:

```python
tracker.update(room, count)
```

Replace it with:

```python
tracker.update(room, count, source="image_upload")
```

Find the webcam tracker update block:

```python
tracker.update(
    room,
    live_count,
    timestamp=live_timestamp
)
```

Replace it with:

```python
tracker.update(
    room,
    live_count,
    timestamp=live_timestamp,
    source="webcam"
)
```

If your current app uses different variable names, preserve those names and add the `source=` argument to the matching tracker call.

## 5. Save and test

Save `history_dashboard.py` and `app.py` with Ctrl+S. In your `(.venv)` terminal run:

```powershell
python -m py_compile app.py history_dashboard.py occupancy_tracker.py
python test_sqlite_tracker.py
```

If both succeed, restart Streamlit:

```powershell
streamlit run app.py
```

The new section should appear at the bottom of the dashboard. It displays each room's latest status, saved observations, a room filter, and an occupancy trend chart.

## Notes

- The dashboard reads records from the existing local `occupancy.db`.
- Existing observations with source `unknown` remain valid; the new source labels apply to new observations.
- The 5-minute freshness threshold is currently set to 300 seconds in the dashboard. Keep it aligned with the recommender's freshness rule.
- AI-detected people are estimates, not verified headcounts.
- This database is local to this computer. Shared hosted data will be a later deployment milestone.
