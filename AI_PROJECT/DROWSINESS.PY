import cv2
import dlib
from scipy.spatial import distance
from imutils import face_utils
import threading
from playsound import playsound

def alarm():
    playsound("alarm.mp3")

def EAR(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 20
counter = 0

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

def run_drowsiness(frame):
    global counter

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]

        ear = (EAR(leftEye) + EAR(rightEye)) / 2.0

        if ear < EYE_AR_THRESH:
            counter += 1
            if counter >= EYE_AR_CONSEC_FRAMES:
                threading.Thread(target=alarm).start()
                return True
        else:
            counter = 0

    return False