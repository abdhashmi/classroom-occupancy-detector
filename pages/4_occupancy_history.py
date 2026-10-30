
import streamlit as st

from classrooms import classrooms
from occupancy_tracker import OccupancyTracker
from history_dashboard import render_occupancy_history

st.set_page_config(
    page_title="Occupancy History",
    page_icon="📈",
    layout="wide",
)

st.title("Occupancy History & Trends")
st.caption("Review saved observations, timestamps, and occupancy trends.")

if "occupancy_tracker" not in st.session_state:
    st.session_state.occupancy_tracker = OccupancyTracker()

tracker = st.session_state.occupancy_tracker

render_occupancy_history(tracker, classrooms)
