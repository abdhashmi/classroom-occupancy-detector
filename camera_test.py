
import cv2

for camera_index in [0, 1, 2]:
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if cap.isOpened():
        success, frame = cap.read()

        if success:
            print(f"Camera {camera_index} works. Frame: {frame.shape}")
            cv2.imshow("Camera Test", frame)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
            cap.release()
            break

        print(f"Camera {camera_index} opened but returned no frame.")
    else:
        print(f"Camera {camera_index} could not be opened.")

    cap.release()
else:
    print("No working camera found.")