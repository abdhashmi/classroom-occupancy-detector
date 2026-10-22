import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO

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


st.title("Intelligent Classroom Occupancy Agent")
st.caption("AI-based classroom monitoring and utilization analysis")

with st.sidebar:
    st.header("Configuration")

    room = st.selectbox(
        "Select classroom",
        list(classrooms.keys())
    )

    analysis_time = st.time_input(
        "Observation time"
    )

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

    with st.spinner("Detecting people in the classroom..."):
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
        annotated = result.plot()
        annotated = cv2.cvtColor(
            annotated,
            cv2.COLOR_BGR2RGB
        )

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
            if schedule else analysis_time.strftime("%H:%M")
        )
    )

    expected = (
        schedule["expected_students"]
        if schedule else None
    )

    attendance_status = (
        agent.check_attendance(count, expected)
        if schedule else "NO_CLASS_SCHEDULED"
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

    st.divider()

    left, right = st.columns([3, 2])

    with left:
        st.subheader("Detection Results")
        st.image(
            annotated,
            caption="YOLO person detections",
            use_container_width=True
        )

    with right:
        st.subheader("Classroom Status")

        st.write(f"**Building:** {room_info['building']}")
        st.write(f"**Floor:** {room_info['floor']}")
        st.write(f"**Room type:** {room_info['type']}")
        st.write(
            f"**Timetable:** {'Class scheduled' if scheduled else 'No class scheduled'}"
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
    st.info("Upload a classroom image to begin analysis.")

    st.subheader("Registered Classrooms")

    for room_id, info in classrooms.items():
        st.write(
            f"**{room_id}** — {info['building']}, "
            f"Floor {info['floor']}, Capacity {info['capacity']}, "
            f"Type: {info['type']}"
        )
