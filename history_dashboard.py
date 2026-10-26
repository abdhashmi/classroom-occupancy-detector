from datetime import datetime

import pandas as pd
import streamlit as st


def render_occupancy_history(tracker, classrooms):
    """Render current room occupancy and historical SQLite observations."""
    st.divider()
    st.header("Occupancy History & Trends")
    st.caption(
        "Counts are AI detections, not verified headcounts. "
        "A missing or stale observation means occupancy is unknown."
    )

    latest = tracker.observations
    now = datetime.now()
    freshness_seconds = 300

    st.subheader("Latest status by room")
    latest_rows = []

    for room_id, info in classrooms.items():
        observation = latest.get(room_id)
        capacity = info.get("capacity", 0)

        if observation is None:
            detected = None
            timestamp = None
            status = "UNVERIFIED"
            remaining = None
        else:
            detected = observation["count"]
            timestamp = observation["timestamp"]
            age = (now - timestamp).total_seconds()

            if age < 0 or age > freshness_seconds:
                status = "STALE"
                remaining = None
            else:
                remaining = max(capacity - detected, 0)
                if detected > capacity:
                    status = "OVER CAPACITY"
                elif detected == 0:
                    status = "EMPTY (OBSERVED)"
                else:
                    status = "OCCUPIED"

        latest_rows.append({
            "Room": room_id,
            "Building": info.get("building", "—"),
            "Floor": str(info.get("floor", "—")),
            "Room type": info.get("type", "—"),
            "Capacity": str(capacity),
            "Detected people": str(detected) if detected is not None else "Unknown",
            "Remaining seats": str(remaining) if remaining is not None else "Unknown",
            "Last observation": timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "Never",
            "Status": status,
        })

    st.dataframe(pd.DataFrame(latest_rows), use_container_width=True, hide_index=True)

    st.subheader("Observation history")
    room_options = ["All rooms"] + list(classrooms.keys())
    selected_room = st.selectbox(
        "Filter history by room", room_options, key="occupancy_history_room_filter"
    )
    limit = st.selectbox(
        "Maximum records to display",
        [25, 50, 100, 250, 500],
        index=2,
        key="occupancy_history_limit",
    )

    history = tracker.get_history(
        room=None if selected_room == "All rooms" else selected_room,
        limit=limit,
    )

    if not history:
        st.info(
            "No observations have been saved yet. Upload a classroom image "
            "or start the webcam to create the first record."
        )
        return

    history_rows = []
    for item in history:
        room_info = classrooms.get(item["room"], {})
        capacity = room_info.get("capacity")
        count = item["count"]
        history_rows.append({
            "Timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "Room": item["room"],
            "Detected people": str(count),
            "Room capacity": str(capacity) if capacity is not None else "Unknown",
            "Remaining seats": str(max(capacity - count, 0)) if capacity is not None else "Unknown",
            "Source": item.get("source", "unknown"),
        })

    st.dataframe(pd.DataFrame(history_rows), use_container_width=True, hide_index=True)

    st.subheader("Occupancy trend")
    trend_room = st.selectbox(
        "Room for trend chart", list(classrooms.keys()), key="occupancy_history_trend_room"
    )
    trend_history = tracker.get_history(room=trend_room, limit=500)

    if not trend_history:
        st.info(f"No history is available for {trend_room} yet.")
        return

    trend_df = pd.DataFrame([
        {"Timestamp": item["timestamp"], "Detected people": int(item["count"])}
        for item in trend_history
    ])
    trend_df = trend_df.sort_values("Timestamp").set_index("Timestamp")
    st.line_chart(trend_df["Detected people"])

    capacity = classrooms.get(trend_room, {}).get("capacity")
    if capacity:
        st.caption(
            f"{trend_room} registered capacity: {capacity}. "
            "Values above capacity should be reviewed as possible detection errors "
            "or overcrowding."
        )
