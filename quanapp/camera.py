import cv2
import dlib
from imutils import face_utils
import time

from sqlalchemy import false
from quanapp.base_camera import BaseCamera
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("quanapp/shape_predictor_68_face_landmarks.dat")

class Camera1(BaseCamera):
    lst = [0]
    video_source = 0
    video_crop = False

    def set_video_source(source):
        Camera1.video_source = source

    def set_video_crop(cropped):
        Camera1.video_crop = cropped

    def frames():
        camera = cv2.VideoCapture(Camera1.video_source)
        while True:
            success, image = camera.read()
            width, height = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)), int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            if not success:
                print("Webcam fail: ", Camera1.video_source)
                break
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                start = time.time()
                rects = detector(gray, 0)
                for (i, rect) in enumerate(rects):
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    for(x, y) in shape:
                        cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
                    if Camera1.video_crop:
                        minx, miny, maxx, maxy = width, height, 0, 0
                        for(x, y) in shape:
                            if(minx>x): minx = x
                            if(miny>y): miny = y
                            if(maxx<x): maxx = x
                            if(maxy<y): maxy = y
                        image = image[miny-10:maxy+10, minx-10:maxx+10]
                end = time.time()
                ret, buffer = cv2.imencode(".jpg", image)
                k = 1/(end-start)
                Camera1.lst.append(k)
                yield buffer.tobytes()
            c = cv2.waitKey(0)
            if c == 27:
                break
        camera.release()


class Camera2(BaseCamera):
    lst = [0]
    video_source = 0
    video_crop = False

    def set_video_source(source):
        Camera2.video_source = source

    def set_video_crop(cropped):
        Camera2.video_crop = cropped

    def frames():
        camera = cv2.VideoCapture(Camera2.video_source)
        while True:
            success, image = camera.read()
            width, height = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)), int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            if not success:
                print("Webcam fail: ", Camera2.video_source)
                break
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                start = time.time()
                rects = detector(gray, 0)
                for (i, rect) in enumerate(rects):
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    for(x, y) in shape:
                        cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
                    if Camera2.video_crop:
                        minx, miny, maxx, maxy = width, height, 0, 0
                        for(x, y) in shape:
                            if(minx>x): minx = x
                            if(miny>y): miny = y
                            if(maxx<x): maxx = x
                            if(maxy<y): maxy = y
                        image = image[miny-10:maxy+10, minx-10:maxx+10]
                end = time.time()
                ret, buffer = cv2.imencode(".jpg", image)
                k = 1/(end-start)
                Camera2.lst.append(k)
                yield buffer.tobytes()
            c = cv2.waitKey(0)
            if c == 27:
                break
        camera.release()

