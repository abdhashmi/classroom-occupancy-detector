
from ultralytics import YOLO
import cv2

from agent import ClassroomAgent
from classrooms import classrooms
from timetable import get_schedule


ROOM = "VED226"
CAMERA_INDEX = 0


def run_monitor():
    room_info = classrooms[ROOM]

    agent = ClassroomAgent(
        ROOM,
        room_info["capacity"]
    )

    model = YOLO("yolo26n.pt")
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    try:
        while True:
            success, frame = cap.read()

            if not success:
                print("Error: Could not read camera frame.")
                break

            result = model.predict(
                frame,
                classes=[0],
                conf=0.35,
                verbose=False
            )[0]

            count = len(result.boxes)
            annotated = result.plot()

            now = cv2.getTickCount() / cv2.getTickFrequency()
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M")

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

            expected = (
                schedule["expected_students"]
                if schedule else None
            )

            attendance = (
                agent.check_attendance(count, expected)
                if schedule else "NO CLASS SCHEDULED"
            )

            cv2.putText(
                annotated,
                f"Room: {ROOM} | Detected: {count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

            cv2.putText(
                annotated,
                f"Capacity: {room_info['capacity']} | State: {state}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2
            )

            cv2.putText(
                annotated,
                f"Timetable: {'Scheduled' if scheduled else 'No class'}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 0),
                2
            )

            cv2.imshow("Intelligent Classroom Agent", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

        print(f"Total observations: {len(agent.history)}")


if __name__ == "__main__":
    run_monitor()
