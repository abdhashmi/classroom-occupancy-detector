
from ultralytics import YOLO
import cv2
from pathlib import Path

from agent import ClassroomAgent
from classrooms import classrooms
from timetable import get_schedule


ROOM = "VED226"
IMAGE_PATH = input("Enter classroom image path: ").strip().strip('"')

image_path = Path(IMAGE_PATH)

if not image_path.is_file():
    raise FileNotFoundError(f"Image not found: {image_path}")

image = cv2.imread(str(image_path))

if image is None:
    raise ValueError("Could not read the image.")

model = YOLO("yolo26n.pt")

result = model.predict(
    image,
    classes=[0],
    conf=0.30,
    imgsz=1280,
    iou=0.50,
    max_det=100,
    verbose=False
)[0]

count = len(result.boxes)
annotated = result.plot()

room_info = classrooms[ROOM]
agent = ClassroomAgent(ROOM, room_info["capacity"])

current_time = input("Enter time (HH:MM): ").strip()

schedule = get_schedule(ROOM, current_time)
scheduled = schedule is not None

state = agent.observe(
    count,
    scheduled,
    period=(
        (schedule["start"], schedule["end"])
        if schedule else current_time
    )
)

expected = schedule["expected_students"] if schedule else None

print("\n--- Classroom Analysis ---")
print(f"Room: {ROOM}")
print(f"Detected people: {count}")
print(f"Capacity: {room_info['capacity']}")
print(f"Timetable status: {'Scheduled' if scheduled else 'No class scheduled'}")
print(f"Expected students: {expected if expected is not None else 'N/A'}")
print(f"Classroom state: {state}")

if schedule:
    print(
        "Attendance check:",
        agent.check_attendance(count, expected)
    )

cv2.putText(
    annotated,
    f"Room: {ROOM} | People: {count}",
    (15, 30),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 255, 0),
    2
)

cv2.imshow("Classroom Image Analysis", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()
