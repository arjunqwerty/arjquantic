from imutils import face_utils
import cv2
import dlib

p = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(p)

cap = cv2.VideoCapture(0)
while True:
    _, image = cap.read()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)

    for (i, rect) in enumerate(rects):
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        
        for(x, y) in shape:
            cv2.circle(image, (x, y), 2, (0, 255, 0), -1)

    cv2.imshow("Output", image)

    k = cv2.waitKey(5) & 0xFF
    print(k, end=" ")
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
