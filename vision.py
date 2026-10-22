from ultralytics import YOLO
import cv2


def run_video():
    model = YOLO("yolo26n.pt")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Error: Could not open camera 0.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        while True:
            success, frame = cap.read()

            if not success:
                print("Warning: Could not read camera frame.")
                break

            result = model.predict(
                frame,
                classes=[0],
                conf=0.35,
                verbose=False
            )[0]

            count = len(result.boxes)
            annotated = result.plot()

            cv2.putText(
                annotated,
                f"People detected: {count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.imshow("Classroom Occupancy Detection", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_video()