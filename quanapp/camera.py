import cv2
import dlib
from imutils import face_utils
import time

from sqlalchemy import false
from quanapp.base_camera import BaseCamera
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("quanapp/shape_predictor_68_face_landmarks.dat")

class Camera(BaseCamera):
    lst = [[0],[0]]
    video_source = 0
    video_crop = False

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def set_video_crop(cropped=False):
        Camera.video_crop = cropped

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        while True:
            success, image = camera.read()
            if not success:
                print("Webcam fail: ", Camera.video_source)
                break
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                start = time.time()
                rects = detector(gray, 0)
                for (i, rect) in enumerate(rects):
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    minx, miny, maxx, maxy = 10000, 10000, 0, 0
                    for(x, y) in shape:
                        if Camera.video_crop:
                            if(minx>x): minx = x
                            if(miny>y): miny = y
                            if(maxx<x): maxx = x
                            if(maxy<y): maxy = y
                        cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
                if Camera.video_crop:
                    image = image[miny-10:maxy+10, minx-10:maxx+10]
                end = time.time()
                ret, buffer = cv2.imencode(".jpg", image)
                k = 1/(end-start)
                Camera.lst[Camera.video_source].append(k)
                yield buffer.tobytes()
            c = cv2.waitKey(0)
            if c == 27:
                break
        camera.release()

