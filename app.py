import threading
from datetime import datetime, timedelta

import av
import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from agent import ClassroomAgent
from classrooms import classrooms
from history_dashboard import render_occupancy_history
from occupancy_tracker import OccupancyTracker
from availability_service import search_availability
from timetable import timetable as timetable_entries


st.set_page_config(
    page_title="Intelligent Classroom Agent",
    page_icon="🏫",
    layout="wide",
)


@st.cache_resource
def load_model():
    return YOLO("yolo26n.pt")


class LivePersonDetector(VideoProcessorBase):
    def __init__(self):
        self.model = load_model()
        self.lock = threading.Lock()
        self.latest_count = None
        self.latest_time = None
        self.confidence = 0.30
        self.image_size = 1280

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        result = self.model.predict(
            image,
            classes=[0],
            conf=self.confidence,
            imgsz=self.image_size,
            iou=0.50,
            max_det=100,
            verbose=False,
        )[0]

        count = len(result.boxes)
        annotated = result.plot()

        cv2.rectangle(annotated, (10, 10), (360, 65), (0, 0, 0), -1)
        cv2.putText(
            annotated,
            f"People detected: {count}",
            (20, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        with self.lock:
            self.latest_count = count
            self.latest_time = datetime.now()

        return av.VideoFrame.from_ndarray(annotated, format="bgr24")


st.title("Intelligent Classroom Occupancy Agent")
st.caption("AI-based classroom monitoring and utilization analysis")

if "occupancy_tracker" not in st.session_state:
    st.session_state.occupancy_tracker = OccupancyTracker()
if "live_counts" not in st.session_state:
    st.session_state.live_counts = {}

tracker = st.session_state.occupancy_tracker

with st.sidebar:
    st.header("Configuration")
    room = st.selectbox("Select classroom", list(classrooms.keys()))
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    today_name = datetime.now().strftime("%A")
    default_day_index = weekdays.index(today_name) if today_name in weekdays else 0
    analysis_day = st.selectbox(
        "Timetable weekday",
        weekdays,
        index=default_day_index,
        key="occupancy_analysis_day",
        help="Select the weekday to look up the room's S/R/T timetable entry.",
    )
    analysis_time = st.time_input(
        "Evaluation time",
        value=datetime.now().time().replace(second=0, microsecond=0),
        key="occupancy_analysis_time",
    )
    confidence = st.slider(
        "Detection confidence", 0.10, 0.70, 0.30, 0.05
    )
    image_size = st.selectbox(
        "Detection image size", [640, 960, 1280], index=2
    )

mode = st.radio(
    "Monitoring mode",
    ["Upload Image", "Live Webcam"],
    horizontal=True,
)

count = None
annotated = None
source_available = False
observation_timestamp = None

if mode == "Upload Image":
    uploaded_file = st.file_uploader(
        "Upload a classroom image",
        type=["jpg", "jpeg", "png"],
    )
    if uploaded_file is not None:
        file_bytes = np.frombuffer(
            uploaded_file.getvalue(), dtype=np.uint8
        )
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            st.error("Unable to read this image.")
            st.stop()

        with st.spinner("Detecting people..."):
            result = load_model().predict(
                image,
                classes=[0],
                conf=confidence,
                imgsz=image_size,
                iou=0.50,
                max_det=100,
                verbose=False,
            )[0]
            count = len(result.boxes)
            annotated = cv2.cvtColor(
                result.plot(), cv2.COLOR_BGR2RGB
            )

        observation_timestamp = datetime.now()
        tracker.update(
            room,
            count,
            timestamp=observation_timestamp,
            source="image_upload",
        )
        source_available = True

else:
    st.info(
        "Allow camera access when prompted. "
        "The camera monitors the selected classroom."
    )
    webrtc_ctx = webrtc_streamer(
        key=f"classroom-camera-{room}",
        video_processor_factory=LivePersonDetector,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    if webrtc_ctx.video_processor:
        processor = webrtc_ctx.video_processor
        processor.confidence = confidence
        processor.image_size = image_size

        with processor.lock:
            live_count = processor.latest_count
            live_timestamp = processor.latest_time

        if live_count is not None and live_timestamp is not None:
            st.metric("Live people detected", live_count)
            st.caption(
                f"Last frame processed: {live_timestamp.strftime('%H:%M:%S')}"
            )
            st.session_state.live_counts[room] = {
                "count": live_count,
                "timestamp": live_timestamp,
            }

            tracker.update(
                room,
                live_count,
                timestamp=live_timestamp,
                source="webcam",
            )
            count = live_count
            observation_timestamp = live_timestamp
            source_available = True

            if datetime.now() - live_timestamp > timedelta(seconds=30):
                st.warning(
                    "The last webcam observation is stale. "
                    "Check the camera connection."
                )

if source_available and count is not None:
    room_info = classrooms[room]
    selected_time = analysis_time.strftime("%H:%M")
    matching_schedules = [
        entry for entry in timetable_entries
        if entry["room"] == room
        and entry["day"] == analysis_day
        and entry["start"] <= selected_time < entry["end"]
    ]
    schedule = matching_schedules[0] if matching_schedules else None
    scheduled = bool(matching_schedules)

    observation_age = (
        datetime.now() - observation_timestamp
    ).total_seconds()
    fresh = 0 <= observation_age <= 300

    agent = ClassroomAgent(room, room_info["capacity"])
    state = agent.observe(
        count,
        scheduled,
        period=(
            (schedule["start"], schedule["end"])
            if schedule
            else selected_time
        ),
        fresh=fresh,
    )

    expected = schedule.get("expected_students") if schedule else None
    st.subheader(f"Classroom: {room}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("People detected", count)
    col2.metric("Room capacity", room_info["capacity"])
    col3.metric(
        "Capacity utilization",
        f"{count / room_info['capacity'] * 100:.1f}%",
    )
    col4.metric(
        "Expected attendance",
        expected if expected is not None else "N/A",
    )

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Detection Results")
        if annotated is not None:
            st.image(
                annotated,
                caption="YOLO person detections",
                use_container_width=True,
            )
        elif mode == "Live Webcam":
            st.caption(
                "Live annotated video is displayed in the camera panel above."
            )

    with right:
        st.subheader("Classroom Status")
        st.write(f"**Building:** {room_info['building']}")
        st.write(f"**Floor:** {room_info['floor']}")
        st.write(f"**Room type:** {room_info['type']}")
        st.write(f"**Timetable weekday:** {analysis_day}")
        st.write(f"**Evaluation time:** {selected_time}")
        st.write(
            f"**Timetable:** "
            f"{'Class scheduled' if scheduled else 'No class scheduled'}"
        )
        st.write(f"**Current state:** {state}")
        st.subheader("Scheduled class details")
        if matching_schedules:
            for class_entry in matching_schedules:
                class_kind = (
                    "Laboratory (Lab)"
                    if class_entry["type"] == "laboratory"
                    else "Theory (Classroom)"
                )
                st.write(f"**Section:** {class_entry['section']}")
                st.write(
                    f"**Subject:** {class_entry['subject']} "
                    f"({class_entry['subject_code']})"
                )
                st.write(
                    f"**Teacher:** {class_entry['teacher'] or 'Not listed in timetable'}"
                )
                st.write(f"**Class type:** {class_kind}")
                st.write(
                    f"**Scheduled time:** {class_entry['start']}–{class_entry['end']}"
                )
                if len(matching_schedules) > 1:
                    st.divider()
        else:
            st.info(
                f"No S/R/T class is listed for {room} on {analysis_day} "
                f"at {selected_time}."
            )

        if state == "UNKNOWN":
            st.warning(
                "Occupancy is unknown because the observation is invalid or stale."
            )
        elif state == "OVER_CAPACITY":
            st.error("Overcrowding detected.")
        elif state == "UNSCHEDULED_USAGE":
            st.warning("People are present although no class is scheduled.")
        elif state == "OCCUPIED":
            st.info("People are present in a scheduled room.")
        elif state == "SCHEDULED_EMPTY":
            st.warning(
                "The room is scheduled, but no people were detected. "
                "It is not considered available."
            )
        elif state == "AVAILABLE":
            st.success(
                "The room was observed empty and has no class scheduled "
                "at the selected evaluation time."
            )

        if schedule and expected is not None:
            absent_count = max(expected - count, 0)
            present_col, absent_col = st.columns(2)
            present_col.metric("Present", count)
            absent_col.metric("Absent", absent_count)
else:
    st.info("Start the webcam or upload an image to analyze occupancy.")

st.divider()
st.header("Classroom Availability Search")
st.caption(
    "Search a one-hour slot Monday-Friday. Timetable conflicts are checked "
    "for sections S, R, and T. Rooms absent from the timetable are eligible "
    "for consideration, but camera evidence may still be missing or stale."
)

search_col1, search_col2, search_col3, search_col4 = st.columns(4)
with search_col1:
    search_day = st.selectbox(
        "Requested weekday",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        index=None,
        placeholder="Select the day",
        key="availability_day",
    )
with search_col2:
    preferred_search_room = st.selectbox(
        "Preferred classroom",
        list(classrooms.keys()),
        index=None,
        placeholder="Search or select classroom",
        key="availability_preferred_room",
    )
with search_col3:
    search_start_text = st.text_input(
        "One-hour slot starts at",
        value="",
        placeholder="Enter time (HH:MM)",
        key="availability_start_text",
    )
with search_col4:
    required_capacity = st.number_input(
        "Required capacity",
        min_value=1,
        max_value=500,
        value=35,
        step=1,
        key="availability_capacity",
    )

room_types = ["classroom", "laboratory"]
required_type = st.selectbox(
    "Required room type",
    room_types,
    index=None,
    placeholder="Select room type",
    key="availability_room_type",
)

if st.button("Search Availability", type="primary"):
    if not search_day:
        st.error("Select a weekday.")
        st.stop()
    if not preferred_search_room:
        st.error("Search for or select a preferred classroom.")
        st.stop()
    if not search_start_text.strip():
        st.error("Enter a start time in HH:MM format.")
        st.stop()
    if not required_type:
        st.error("Select a room type.")
        st.stop()
    try:
        search_start = datetime.strptime(search_start_text.strip(), "%H:%M").time()
    except ValueError:
        st.error("Invalid time. Enter it in 24-hour HH:MM format, for example 09:00 or 14:30.")
        st.stop()

    start_dt = datetime.now().replace(
        hour=search_start.hour,
        minute=search_start.minute,
        second=0,
        microsecond=0,
    )
    end_dt = start_dt + timedelta(hours=1)
    start_text = start_dt.strftime("%H:%M")
    end_text = end_dt.strftime("%H:%M")

    try:
        result = search_availability(
            preferred_room=preferred_search_room,
            day=search_day,
            start_time=start_text,
            end_time=end_text,
            required_capacity=int(required_capacity),
            required_type=required_type,
            tracker=tracker,
            now=datetime.now(),
            max_age_seconds=300,
        )
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.subheader(f"Search: {search_day}, {start_text}–{end_text}")
    st.write(
        f"**Preferred room:** {preferred_search_room}  ·  "
        f"**Building:** {classrooms[preferred_search_room]['building']}  ·  "
        f"**Floor:** {classrooms[preferred_search_room]['floor']}"
    )

    if result["preferred_room_has_timetable_conflict"]:
        st.error("The preferred room has a scheduled class during this time.")
    else:
        st.info("No S/R/T timetable class is recorded in the preferred room for this slot.")

    st.subheader("Section-wise scheduled classes")
    if result["scheduled_classes"]:
        schedule_rows = [
            {
                "Section": entry["section"],
                "Day": entry["day"],
                "Time": f"{entry['start']}–{entry['end']}",
                "Room": entry["room"],
                "Subject": entry["subject"],
                "Subject code": entry["subject_code"],
                "Teacher": entry["teacher"] or "Not listed",
                "Class type": entry["type"],
            }
            for entry in result["scheduled_classes"]
        ]
        st.dataframe(schedule_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No S/R/T timetable classes are recorded for this time slot.")

    st.subheader("Recently observed empty — best alternatives")
    available = result["available"]
    if available:
        for index, item in enumerate(available, start=1):
            with st.container(border=True):
                st.markdown(f"**{index}. {item['room']}** — {item['building']}, Floor {item['floor']}")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Capacity", item["capacity"])
                col2.metric("Detected people", item["observed_count"])
                col3.metric("Walking time", f"{item['walking_minutes']} min")
                col4.metric("Seats remaining", item["remaining_seats"])
                st.caption(
                    f"Latest observation: {item['observed_at'].strftime('%Y-%m-%d %H:%M:%S')} "
                    f"({item['observation_source'] or 'source unknown'}). "
                    f"Route estimate: {item['route']}."
                )
    else:
        st.info(
            "No suitable alternative has both no timetable conflict and a recent "
            "zero-person observation. Check the unverified rooms below."
        )

    st.subheader("Unverified alternatives")
    unverified = result["unverified"]
    if unverified:
        st.warning(
            "These rooms have no recent valid observation. They are not confirmed "
            "available and should be checked before use."
        )
        unverified_rows = [
            {
                "Room": item["room"],
                "Building": item["building"],
                "Floor": item["floor"],
                "Capacity": item["capacity"],
                "Type": item["type"],
                "Status": item["status"],
                "Walking time (min)": item["walking_minutes"],
                "Route estimate": item["route"],
            }
            for item in unverified
        ]
        st.dataframe(unverified_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No unverified rooms match the selected capacity and room type.")

    st.subheader("Recently observed occupied")
    occupied = result["occupied"]
    if occupied:
        occupied_rows = [
            {
                "Room": item["room"],
                "Building": item["building"],
                "Floor": item["floor"],
                "Capacity": item["capacity"],
                "Detected people": item["observed_count"],
                "Seats remaining": item["remaining_seats"],
                "Walking time (min)": item["walking_minutes"],
            }
            for item in occupied
        ]
        st.dataframe(occupied_rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No matching rooms have a recent observation showing people.")

    if result["excluded_by_timetable"]:
        with st.expander("Rooms excluded because a class is scheduled"):
            conflict_rows = []
            for room_conflict in result["excluded_by_timetable"]:
                for entry in room_conflict["classes"]:
                    conflict_rows.append({
                        "Room": room_conflict["room"],
                        "Section": entry["section"],
                        "Subject": entry["subject"],
                        "Time": f"{entry['start']}–{entry['end']}",
                        "Teacher": entry["teacher"] or "Not listed",
                        "Class type": entry["type"],
                    })
            st.dataframe(conflict_rows, use_container_width=True, hide_index=True)

    st.caption(
        "Availability is based on the supplied S/R/T timetable and camera observations "
        "no older than five minutes. It does not account for unrecorded classes, "
        "reservations, or changes after the last observation. Walking times are estimates."
    )
