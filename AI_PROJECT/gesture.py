import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)

def run_gesture():
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        h, w, c = img.shape

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                for id, lm in enumerate(hand.landmark):
                    if id == 8:  # index finger tip
                        x = int(lm.x * w)
                        y = int(lm.y * h)

                        screen_x = int(lm.x * screen_w)
                        screen_y = int(lm.y * screen_h)

                        pyautogui.moveTo(screen_x, screen_y)

                        cv2.circle(img, (x, y), 10, (0, 255, 255), -1)

                mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Gesture Control", img)
        if cv2.waitKey(1) == 27:
            break