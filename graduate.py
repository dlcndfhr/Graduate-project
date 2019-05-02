import time
import numpy as np
import winsound as ws
import cv2
import dlib
import serial
from scipy.spatial import distance as dist


PREDICTOR_PATH = 'shape_predictor_68_face_landmarks.dat'
####여기서 눈 뺴고는 필요 없는 것인지 확인해보자####
FULL_POINTS = list(range(0, 68))
FACE_POINTS = list(range(17, 68))

JAWLINE_POINTS = list(range(0, 17))
RIGHT_EYEBROW_POINTS = list(range(17, 22))
LEFT_EYEBROW_POINTS = list(range(22, 27))
NOSE_POINTS = list(range(27, 36))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
MOUTH_OUTLINE_POINTS = list(range(48, 61))
MOUTH_INNER_POINTS = list(range(61, 68))

####################초기 변수 값들 설정########################
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 3

COUNTER_LEFT = 0
TOTAL_LEFT = 0

COUNTER_RIGHT = 0
TOTAL_RIGHT = 0

COUNTER = 0
COUNTER_FRAME = 48
##############################################################

#####################################눈 크기 구하는 함수(유클리드 거리계산 공식사용)##############################
########eye[x]부분 왜 그런것인가?##########
def eye_aspect_ratio(eye):

    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)

    return ear
###################################################################################################################

###################################################################################################################
def beepsound():
    freq =2000 #range : 37~ 32767
    dur = 1000 #ms
    ws.Beep(freq , dur)

detector = dlib.get_frontal_face_detector()          ## dlib 에서 가져온게 무었인지 알 필요가 있음

predictor = dlib.shape_predictor(PREDICTOR_PATH)     ## dlib 에서 가져온게 무었인지 알 필요가 있음

# Start capturing the WebCam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()

    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        for rect in rects:
            x = rect.left()
            y = rect.top()
            x1 = rect.right()
            y1 = rect.bottom()

            landmarks = np.matrix([[p.x, p.y] for p in predictor(frame, rect).parts()])

            left_eye = landmarks[LEFT_EYE_POINTS]
            right_eye = landmarks[RIGHT_EYE_POINTS]

            left_eye_hull = cv2.convexHull(left_eye)
            right_eye_hull = cv2.convexHull(right_eye)
            cv2.drawContours(frame, [left_eye_hull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [right_eye_hull], -1, (0, 255, 0), 1)

            ear_left = eye_aspect_ratio(left_eye)     # 위에 정의된 함수를 이용한 왼쪽눈 ear을 변수에 저장
            ear_right = eye_aspect_ratio(right_eye)   # 위에 정의된 함수를 이용한 오른쪽눈 ear을 변수에 저장

            cv2.putText(frame, "E.A.R. Left : {:.2f}".format(ear_left), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 255), 2)     #ear left 텍스트 생성
            cv2.putText(frame, "E.A.R. Right: {:.2f}".format(ear_right), (300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 255), 2)     #ear right 텍스트 생성

            ear = (ear_right + ear_left)/2

            if ear <= EYE_AR_THRESH:
                COUNTER += 1
                if COUNTER >= COUNTER_FRAME:
                    beepsound()
            else:
                COUNTER = 0
#########################################################################################################

            if ear_left < EYE_AR_THRESH:
                COUNTER_LEFT += 1
            else:
                if COUNTER_LEFT >= EYE_AR_CONSEC_FRAMES:
                    TOTAL_LEFT += 1
                    print("Left eye winked")
                COUNTER_LEFT = 0

            if ear_right < EYE_AR_THRESH:
                COUNTER_RIGHT += 1
            else:
                if COUNTER_RIGHT >= EYE_AR_CONSEC_FRAMES:
                    TOTAL_RIGHT += 1
                    print("Right eye winked")
                COUNTER_RIGHT = 0
#########################################################################################################


        cv2.putText(frame, "Wink Left : {}".format(TOTAL_LEFT), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255),
                    2)              #wink left의 텍스트 생성
        cv2.putText(frame, "Wink Right: {}".format(TOTAL_RIGHT), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255),
                    2)              #wink right의 텍스트 생성

        cv2.imshow("Faces found", frame)

        ch = 0xFF & cv2.waitKey(1)

        if ch == ord('q'):
            break

    cv2.destroyAllWindows()