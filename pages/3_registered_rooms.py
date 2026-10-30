
import streamlit as st
import pandas as pd

from classrooms import classrooms

st.set_page_config(
    page_title="Registered Rooms",
    page_icon="🚪",
    layout="wide",
)

st.title("Registered Rooms")
st.caption("Search and filter the registered classrooms and laboratories.")

df = pd.DataFrame([
    {
        "Room": room_id,
        "Building": info["building"],
        "Floor": info["floor"],
        "Capacity": info["capacity"],
        "Type": info["type"],
    }
    for room_id, info in classrooms.items()
])

col1, col2, col3 = st.columns(3)

with col1:
    building = st.selectbox(
        "Building",
        ["All"] + sorted(df["Building"].unique().tolist()),
    )

with col2:
    room_type = st.selectbox(
        "Room type",
        ["All"] + sorted(df["Type"].unique().tolist()),
    )

with col3:
    min_capacity = st.number_input(
        "Minimum capacity",
        min_value=0,
        value=0,
        step=5,
    )

search = st.text_input("Search by room number")

filtered = df.copy()

if building != "All":
    filtered = filtered[filtered["Building"] == building]

if room_type != "All":
    filtered = filtered[filtered["Type"] == room_type]

filtered = filtered[filtered["Capacity"] >= min_capacity]

if search.strip():
    filtered = filtered[
        filtered["Room"].str.contains(search.strip(), case=False)
    ]

st.metric("Matching rooms", len(filtered))
st.dataframe(filtered, use_container_width=True, hide_index=True)
