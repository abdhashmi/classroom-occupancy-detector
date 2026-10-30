
import streamlit as st
import pandas as pd

from timetable import timetable, DAY_NAMES

st.set_page_config(
    page_title="Section Timetables",
    page_icon="📅",
    layout="wide",
)

st.title("Section Timetables")
st.caption("Sections S, R and T · FE-3 and MIN excluded")

section = st.selectbox("Select section", ["S", "R", "T"])

day_options = ["All days"] + list(DAY_NAMES.values())
day = st.selectbox("Select day", day_options)

entries = [
    entry for entry in timetable
    if entry["section"] == section
    and entry["start"] != "13:00"
    and entry["end"] != "14:00"
    and not (entry["start"] < "14:00" and entry["end"] > "13:00")
    and (day == "All days" or entry["day"] == day)
]

if not entries:
    st.info("No timetable entries found for these filters.")
else:
    df = pd.DataFrame(entries)
    columns = [
        "day", "start", "end", "subject_code",
        "subject", "room", "teacher", "type",
    ]
    df = df[columns].sort_values(["day", "start", "room"])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

st.info("13:00–14:00 is reserved for the break.")
