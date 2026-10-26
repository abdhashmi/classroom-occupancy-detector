
import threading
from datetime import datetime, timedelta

import av
import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from occupancy_tracker import OccupancyTracker
from room_recommender import recommend_rooms
from classrooms import classrooms
from agent import ClassroomAgent
from timetable import get_schedule


st.set_page_config(
    page_title="Intelligent Classroom Agent",
    page_icon="🏫",
    layout="wide"
)


@st.cache_resource
def load_model():
    return YOLO("yolo26n.pt")



class LivePersonDetector(VideoProcessorBase):
    def __init__(self):
        self.model = load_model()
        self.lock = threading.Lock()
        self.latest_count = 0
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
            verbose=False
        )[0]

        count = len(result.boxes)
        annotated = result.plot()

        # Display the count directly on the video.
        cv2.rectangle(
            annotated,
            (10, 10),
            (340, 65),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            annotated,
            f"People detected: {count}",
            (20, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        with self.lock:
            self.latest_count = count
            self.latest_time = datetime.now()

        return av.VideoFrame.from_ndarray(
            annotated,
            format="bgr24"
        )


st.title("Intelligent Classroom Occupancy Agent")
st.caption("AI-based classroom monitoring and utilization analysis")

if "occupancy_tracker" not in st.session_state:
    st.session_state.occupancy_tracker = OccupancyTracker()

if "live_counts" not in st.session_state:
    st.session_state.live_counts = {}

tracker = st.session_state.occupancy_tracker

with st.sidebar:
    st.header("Configuration")

    room = st.selectbox(
        "Select classroom",
        list(classrooms.keys())
    )

    analysis_time = st.time_input("Observation time")

    confidence = st.slider(
        "Detection confidence",
        min_value=0.10,
        max_value=0.70,
        value=0.30,
        step=0.05
    )

    image_size = st.selectbox(
        "Detection image size",
        [640, 960, 1280],
        index=2
    )

mode = st.radio(
    "Monitoring mode",
    ["Upload Image", "Live Webcam"],
    horizontal=True
)

count = None
annotated = None
source_available = False

if mode == "Upload Image":
    uploaded_file = st.file_uploader(
        "Upload a classroom image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        file_bytes = np.frombuffer(
            uploaded_file.getvalue(),
            dtype=np.uint8
        )

        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            st.error("Unable to read this image.")
            st.stop()

        with st.spinner("Detecting people..."):
            model = load_model()

            result = model.predict(
                image,
                classes=[0],
                conf=confidence,
                imgsz=image_size,
                iou=0.50,
                max_det=100,
                verbose=False
            )[0]

            count = len(result.boxes)
            annotated = cv2.cvtColor(
                result.plot(),
                cv2.COLOR_BGR2RGB
            )

        tracker.update(room, count)
        source_available = True

else:
    st.info(
        "Allow camera access when your browser asks. "
        "The camera monitors the classroom selected in the sidebar."
    )

    webrtc_ctx = webrtc_streamer(
        key=f"classroom-camera-{room}",
        video_processor_factory=LivePersonDetector,
        media_stream_constraints={
            "video": True,
            "audio": False
        },
        async_processing=True
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
                f"Last frame processed: "
                f"{live_timestamp.strftime('%H:%M:%S')}"
            )

            st.session_state.live_counts[room] = {
                "count": live_count,
                "timestamp": live_timestamp
            }

            # Update the occupancy tracker with the actual
            # timestamp of the latest processed frame.
            tracker.update(
                room,
                live_count,
                timestamp=live_timestamp
            )

            count = live_count
            source_available = True

            if datetime.now() - live_timestamp > timedelta(seconds=30):
                st.warning(
                    "The last webcam observation is stale. "
                    "Check the camera connection."
                )

if source_available and count is not None:
    room_info = classrooms[room]

    schedule = get_schedule(
        room,
        analysis_time.strftime("%H:%M")
    )

    scheduled = schedule is not None

    agent = ClassroomAgent(
        room,
        room_info["capacity"]
    )

    state = agent.observe(
        count,
        scheduled,
        period=(
            (schedule["start"], schedule["end"])
            if schedule
            else analysis_time.strftime("%H:%M")
        )
    )

    expected = (
        schedule["expected_students"]
        if schedule
        else None
    )

    attendance_status = (
        agent.check_attendance(count, expected)
        if schedule
        else "NO_CLASS_SCHEDULED"
    )

    st.subheader(f"Classroom: {room}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("People detected", count)
    col2.metric("Room capacity", room_info["capacity"])
    col3.metric(
        "Capacity utilization",
        f"{count / room_info['capacity'] * 100:.1f}%"
    )
    col4.metric(
        "Expected attendance",
        expected if expected is not None else "N/A"
    )

    left, right = st.columns([3, 2])

    with left:
        st.subheader("Detection Results")

        if annotated is not None:
            st.image(
                annotated,
                caption="YOLO person detections",
                use_container_width=True
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
        st.write(
            f"**Timetable:** "
            f"{'Class scheduled' if scheduled else 'No class scheduled'}"
        )
        st.write(f"**Current state:** {state}")
        st.write(f"**Attendance check:** {attendance_status}")

        if count > room_info["capacity"]:
            st.error("Overcrowding detected.")
        elif not scheduled and count > 0:
            st.warning("Unscheduled classroom usage detected.")
        elif scheduled:
            st.success("A class is scheduled in this room.")
        else:
            st.info("The room appears empty or unused.")

        if schedule:
            difference = expected - count

            if difference > 10:
                st.warning(
                    f"{difference} fewer people detected than expected."
                )
            elif difference < -10:
                st.warning(
                    f"{abs(difference)} more people detected than expected."
                )

else:
    st.info(
        "Start the webcam or upload an image to analyze occupancy."
    )

    st.subheader("Registered Classrooms")

    for room_id, info in classrooms.items():
        st.write(
            f"**{room_id}** — {info['building']}, "
            f"Floor {info['floor']}, Capacity {info['capacity']}, "
            f"Type: {info['type']}"
        )


st.divider()
st.header("Alternative Classroom Recommendations")

st.write(
    "Only rooms with recent occupancy observations, sufficient spare "
    "capacity, compatible room type, and no active timetable booking "
    "are recommended."
)

col_a, col_b = st.columns(2)

with col_a:
    required_capacity = st.number_input(
        "Required seating capacity",
        min_value=1,
        max_value=500,
        value=35,
        step=1
    )

with col_b:
    room_types = ["classroom", "laboratory"]

    required_type = st.selectbox(
        "Required room type",
        room_types,
        index=room_types.index(classrooms[room]["type"]),
        key="recommendation_type"
    )


if st.button("Find Verified Alternative Rooms", type="primary"):
    now = datetime.now()

    observed_counts = {}
    unknown_rooms = []

    for room_id, info in classrooms.items():
        observation = tracker.observations.get(room_id)

        if observation is None:
            unknown_rooms.append(room_id)
            continue

        timestamp = observation["timestamp"]
        age = (now - timestamp).total_seconds()
        observed_count = observation["count"]

        if age < 0 or age > 300:
            unknown_rooms.append(room_id)
            continue

        observed_counts[room_id] = observed_count

    # The selected room is excluded by the recommender.
    # Candidates must have recent data and enough spare seats.
    recently_verified = set(observed_counts)

    recommendations = recommend_rooms(
        unavailable_room=room,
        required_capacity=required_capacity,
        required_type=required_type,
        current_time=analysis_time.strftime("%H:%M"),
        occupied_rooms=set(classrooms) - recently_verified
    )

    # Require enough spare seats for the incoming group.
    recommendations = [
        item for item in recommendations
        if (
            item["room"] in observed_counts
            and classrooms[item["room"]]["capacity"]
            - observed_counts[item["room"]]
            >= required_capacity
        )
    ]

    if recommendations:
        st.success(
            f"Found {len(recommendations)} verified suitable alternative(s)."
        )

        for index, item in enumerate(recommendations, start=1):
            with st.container(border=True):
                st.subheader(f"{index}. {item['room']}")

                col1, col2, col3 = st.columns(3)

                col1.metric("Room capacity", item["capacity"])
                col2.metric(
                    "People currently detected",
                    observed_counts[item["room"]]
                )
                col3.metric(
                    "Spare seats",
                    item["capacity"] - observed_counts[item["room"]]
                )

                st.write(f"**Building:** {item['building']}")
                st.write(f"**Floor:** {item['floor']}")
                st.write(
                    f"**Example route distance:** "
                    f"{item['distance_metres']} m"
                )
                st.write(f"**Route:** {item['route']}")

                st.caption(
                    "Route distances are placeholders until replaced "
                    "with verified campus measurements."
                )

    else:
        st.warning(
            "No verified alternative room currently meets all requirements."
        )

    if unknown_rooms:
        st.info(
            "Rooms with unknown or stale occupancy were excluded: "
            + ", ".join(unknown_rooms)
        )
