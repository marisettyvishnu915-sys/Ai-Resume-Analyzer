import cv2
from gesture import run_gesture
from drowsiness import run_drowsiness

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # Run drowsiness detection
    alert = run_drowsiness(frame)

    if alert:
        cv2.putText(frame, "SLEEP ALERT!", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("AI System", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()