"""Section timetables transcribed from the supplied S, R and T screenshots.

Times are local 24-hour times. FE-3 and MIN are intentionally excluded.
The 13:00-14:00 period is a break. Expected attendance is configured per section.
"""

from datetime import datetime

SUBJECTS = {
    "CSN303": "Computer Networks",
    "CSN304": "Artificial Intelligence",
    "ITN301": "Cyber Security Essentials",
    "CSN361": "Blockchain Technology",
    "CSN371": "Fullstack Development",
    "CSN355": "Cyber Crime Investigation",
    "CDC201": "Aptitude and Soft Skills",
}

DAY_NAMES = {"Mo": "Monday", "Tu": "Tuesday", "We": "Wednesday",
             "Th": "Thursday", "Fr": "Friday"}

EXPECTED_ATTENDANCE = {"R": 58, "S": 54, "T": 52}

def _e(section, day, start, end, code, room, teacher=None, lab=False):
    if room.startswith("VE") and not room.startswith("VED"):
        room = "VED" + room[2:]
    if room.startswith("VED505") and room[-1:] in "ABCDE" and "-" not in room:
        room = room[:-1] + "-" + room[-1:]
    return {
        "section": section, "day": DAY_NAMES[day], "day_code": day,
        "start": start, "end": end, "subject_code": code,
        "subject": SUBJECTS.get(code, code), "room": room,
        "teacher": teacher, "type": "laboratory" if lab else "classroom",
        "expected_students": EXPECTED_ATTENDANCE[section],
    }

# Screenshot columns: 08:00, 09:00, 10:00, 11:00, 12:00, 13:00 (break),
# 14:00, 15:00, 16:00, 17:00. The screenshots are visually dense; only
# legible teaching entries are included here. Verify these against originals.
timetable = [
    # Section S
    _e("S","Mo","09:00","10:00","CSN303","VE226","Mr.Akhiles Pandey"),
    _e("S","Mo","10:00","11:00","CSN361","VE226","Dr. Manmohan Pundir"),
    _e("S","Mo","11:00","12:00","CSN371","VE508","Mr. Sanjay Kumar",True),
    _e("S","Mo","11:00","12:00","CSN304","VE505E","Mrs. Shabnam",True),
    _e("S","Mo","15:00","16:00","CSN371","VE202","Mr. Sanjay Kumar"),
    _e("S","Mo","16:00","17:00","ITN301","VE326","Mr. Deekshant Semwal"),
    _e("S","Tu","09:00","10:00","CSN303","VE505E","Mr. Akhiles Pandey",True),
    _e("S","Tu","09:00","10:00","ITN301","Chanakya Lab 4D","Mr. Deekshant Semwal",True),
    _e("S","Tu","11:00","12:00","CSN361","VE226","Dr. Manmohan Pundir"),
    _e("S","Tu","12:00","13:00","CDC201","VE226", "Dr. Abhishek Sarkar"),
    _e("S","Tu","15:00","16:00","ITN301","VE226","Mr. Deekshant Semwal"),
    _e("S","Tu","16:00","17:00","CSN371","VE226","Mr. Sanjay Kumar"),
    _e("S","We","11:00","12:00","CSN304","VE203","Mrs. Shabnam"),
    _e("S","We","12:00","13:00","ITN301","VE226","Mr. Deekshant Semwal"),
    _e("S","We","15:00","16:00","CSN303","VE229","Mr. Akhiles Pandey"),
    _e("S","We","16:00","17:00","CSN361","VE327","Dr. Manmohan Pundir"),
    _e("S","Th","09:00","10:00","ITN301","VE323B","Mr. Deekshant Semwal",True),
    _e("S","Th","09:00","10:00","CSN303","VE323A","Mr. Akhiles Pandey",True),
    _e("S","Th","11:00","12:00","CSN304","VE229","Mrs. Shabnam"),
    _e("S","Th","15:00","16:00","CSN304","VE505E","Mrs. Shabnam",True),
    _e("S","Th","15:00","16:00","CSN371","VE506","Mr. Sanjay Kumar",True),
    _e("S","Fr","11:00","12:00","CSN304","VE229","Mrs. Shabnam"),
    _e("S","Fr","14:00","15:00","CSN303","VE226","Mr. Akhiles Pandey"),
    # Section R
    _e("R","Mo","10:00","11:00","CSN303","VE227","Mr .Akhiles Pandey"),
    _e("R","Mo","11:00","12:00","CSN304","VE227","Mr. Nishchay"),
    _e("R","Mo","12:00","13:00","ITN301","VE227","Mr. Deekshant Semwal"),
    _e("R","Tu","10:00","11:00","CSN361","VE227","Dr. Manmohan Singh"),
    _e("R","Tu","11:00","12:00","CSN371","VE506","MSK",True),
    _e("R","Tu","11:00","12:00","CSN304","VE505C","Mr. Nishchay",True),
    _e("R","Tu","15:00","16:00","CSN371","VE227","Mr. Sanjay Kumar"),
    _e("R","Tu","16:00","17:00","CSN303","VE227","Mr. Akhiles Pandey"),
    _e("R","We","09:00","10:00","ITN301","VE323A","Mr. Deekshant Semwal",True),
    _e("R","We","09:00","10:00","CSN303","VE323B","Mr. Akhiles Pandey",True),
    _e("R","We","10:00","11:00","CSN361","VE227","Dr. Manmohan Singh"),
    _e("R","We","11:00","12:00","CSN303","VE227","Mr. Akhiles Pandey"),
    _e("R","We","15:00","16:00","CSN304","VE226","Mr. Nishchay"),
    _e("R","We","15:00","16:00","CSN371","VE508","Mr. Sanjay Kumar",True),
    _e("R","Th","10:00","11:00","CSN371","VE227","Mr. Sanjay Kumar"),
    _e("R","Th","11:00","12:00","ITN301","VE227","Mr. Deekshant Semwal"),
    _e("R","Th","15:00","16:00","CSN304","VE227","Mr. Nishchay"),
    _e("R","Fr","09:00","10:00","CSN303","VE512","Mr. Akhiles Pandey",True),
    _e("R","Fr","09:00","10:00","ITN301","VE423","Mr. Deekshant Semwal",True),
    _e("R","Fr","11:00","12:00","ITN301","VE227","Mr. Deekshant Semwal"),
    _e("R","Fr","12:00","13:00","CSN361","VE227","Dr. Manmohan Singh"),
    _e("R","Fr","14:00","15:00","CSN304","VE227","Mr. Nishchay"),
    # Section T
    _e("T","Mo","09:00","10:00","CSN361","VE202","Dr. Manmohan Pundir"),
    _e("T","Mo","10:00","11:00","CSN303","VE202","Dr. Shivankur Thapliyal"),
    _e("T","Mo","11:00","12:00","ITN301","VE302","Mr. Deekshant Semwal"),
    _e("T","Mo","12:00","13:00","CDC201","VE302","Dr. Abhishek Sarkar"),
    _e("T","Mo","15:00","16:00","CSN304","VE226","Mrs. Shabnam"),
    _e("T","Mo","16:00","17:00","CSN355","VE226","Mr. Kapil Dev Sharma"),
    _e("T","Tu","09:00","10:00","CSN304","VE505D","Mrs. Shabnam",True),
    _e("T","Tu","09:00","10:00","CSN355","VE507","Mr. Kapil Dev Sharma",True),
    _e("T","Tu","12:00","13:00","CSN355","VE426","Mr. Kapil Dev Sharma"),
    _e("T","Tu","16:00","17:00","ITN301","VISH401","Mr. Deekshant Semwal"),
    _e("T","We","12:00","13:00","CSN304","VE426","Mrs. Shabnam"),
    _e("T","We","15:00","16:00","ITN301","VE511","Mr. Deekshant Semwal",True),
    _e("T","We","15:00","16:00","CSN303","VE323B","Dr. Shivankur Thapliyal",True),
    _e("T","Th","09:00","10:00","CSN361","VISH402","Dr. Manmohan Pundir"),
    _e("T","Th","10:00","11:00","CSN303","VISH302","Dr. Shivankur Thapliyal"),
    _e("T","Th","15:00","16:00","CSN303","VE425","Dr. Shivankur Thapliyal",True),
    _e("T","Th","15:00","16:00","ITN301","VE423","Mr. Deekshant Semwal",True),
    _e("T","Fr","09:00","10:00","CSN361","VISH406","Dr. Manmohan Pundir"),
    _e("T","Fr","10:00","11:00","CSN304","VISH402","Mrs. Shabnam"),
    _e("T","Fr","11:00","12:00","CSN303","VISH402","Dr. Shivankur Thapliyal"),
    _e("T","Fr","15:00","16:00","CSN355","VE323A","Mr. Kapil Dev Sharma",True),
    _e("T","Fr","15:00","16:00","CSN304","VE202","Mrs. Shabnam",True),
]

def get_schedule(room, current_time=None, day=None, section=None):
    """Return the first matching schedule, retaining the old two-argument API.

    For accurate day-specific lookups, pass day as a weekday name/code.
    If day is omitted, today's weekday is used.
    """
    if current_time is None:
        current_time = datetime.now().strftime("%H:%M")
    if day is None:
        day = datetime.now().strftime("%A")
    day = DAY_NAMES.get(day, day)
    for entry in timetable:
        if (entry["room"] == room
                and entry["start"] <= current_time < entry["end"]
                and entry["day"] == day
                and (section is None or entry["section"] == section)):
            return entry
    return None

def get_section_schedule(section, day=None):
    if day is None:
        day = datetime.now().strftime("%A")
    day = DAY_NAMES.get(day, day)
    return [entry for entry in timetable
            if entry["section"] == section and entry["day"] == day]
