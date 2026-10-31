# Classroom Agent — 15-minute freshness update

This package combines the wording in the `app.py` file you supplied with the
15-minute occupancy freshness setting and the bulk-query performance improvements.

## Files
- `app.py` — based on your supplied wording; your edited availability messages,
  section labels, and descriptions are retained. The freshness threshold now
  uses the shared 15-minute constant.
- `occupancy_tracker.py` — shared SQLite/Neon tracker and central
  `OCCUPANCY_FRESHNESS_SECONDS = 15 * 60` setting.
- `availability_service.py` — optimized bulk occupancy lookup; defaults to the
  same 15-minute freshness setting.
- `history_dashboard.py` — uses the shared freshness setting.
- Test files — focused checks for tracker and availability behavior.

## Apply
1. Stop Streamlit (`Ctrl+C`).
2. Back up `app.py`, `occupancy_tracker.py`, `availability_service.py`, and
   `history_dashboard.py`.
3. Copy these four Python files into the project root, replacing the old files.
4. Do not replace `.streamlit/secrets.toml`, `occupancy.db`, SQLite backups,
   `timetable.py`, `classrooms.py`, or any other project files.
5. Restart with `streamlit run app.py`.

## Notes
- Existing Neon records are not deleted or rewritten.
- The 15-minute threshold changes only whether an observation is considered
  recent; historical records remain stored.
- `app.py` retains the wording present in the supplied source file.
- Do not commit `.streamlit/secrets.toml` or share `DATABASE_URL`.
