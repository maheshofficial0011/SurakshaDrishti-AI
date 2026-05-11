import cv2

for i in range(5):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        print("Working camera index:", i)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Camera Test", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        break

cv2.destroyAllWindows()