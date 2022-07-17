import numpy as np
import cv2
import dlib
from imutils import face_utils

from multiprocessing import Process, Queue
import time

#from common import clock, draw_str, StatValue
#import video
p = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(p)

class Canny_Process(Process):

    def __init__(self,frame_queue,output_queue):
        Process.__init__(self)
        self.frame_queue = frame_queue
        self.output_queue = output_queue
        self.stop = False
        #Initialize your face detectors here

    def get_frame(self):
        if not self.frame_queue.empty():
            return True, self.frame_queue.get()
        else:
            return False, None

    def stopProcess(self):
        self.stop = True

    def canny_frame(self,frame):
        # some intensive computation...
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # edges = cv2.Canny(gray, 50, 100)
        rects = detector(gray, 0)
        for (i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            for(x, y) in shape:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        #To simulate CPU Time
        #############################
        '''for i in range(1000000):
            x = 546*546
            res = x/(i+1)'''
        #############################
        'REPLACE WITH FACE DETECT CODE HERE'

        if self.output_queue.full():
            self.output_queue.get_nowait()
        self.output_queue.put(frame)

    def run(self):
        while not self.stop:
            ret, frame = self.get_frame()
            if ret:
                self.canny_frame(frame)

def process_video(frame_sum):
    def put_frame(frame):
        if Input_Queue.full():
            Input_Queue.get_nowait()
        Input_Queue.put(frame)

    def cap_read(cv2_cap):
        ret, frame = cv2_cap.read()
        if ret:
            put_frame(frame)

    cap = cv2.VideoCapture('video.mp4')

    print("1", end=" ")
    for x in range(threadn):
        canny_process = Canny_Process(frame_queue = Input_Queue,output_queue = Output_Queue)
        canny_process.daemon = True
        canny_process.start()
        process_list.append(canny_process)

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter()
    out.open('multi_vid.mp4', fourcc, 25, (960, 540), True)
    ch = cv2.waitKey(1)
    # cv2.namedWindow('Threaded Video', cv2.WINDOW_NORMAL)
    print("2", end=" ")
    non_frame_sum = 0
    try:
        while True:
            print("3", end=" ")
            cap_read(cap)
            print("4", end=" ")

            if not Output_Queue.empty():
                result = Output_Queue.get()
                out.write(result)
                print(non_frame_sum, end="  ")
                non_frame_sum = 0
                frame_sum = frame_sum + 1
                print(frame_sum)
                # cv2.imshow('Threaded Video', result)
            else:
                non_frame_sum = non_frame_sum + 1
            ch = cv2.waitKey(5)

            print("6", end=" ")
            # if ch == ord(' '):
                # threaded_mode = not threaded_mode
            if ch == 27:
                break
    except:
        cap.release()
        out.release()
    print("7", end=" ")
    cv2.destroyAllWindows()
    cap.release()
    out.release()
    return frame_sum

if __name__ == '__main__':
    process_list = []
    Input_Queue = Queue(maxsize = 5)
    Output_Queue = Queue(maxsize = 5)
    frame_sum = 0
    threadn = 1
    # threaded_mode = True
    start_time = time.time()
    frame_sum = process_video(frame_sum)
    end_time = time.time()
    total_processing_time = end_time - start_time
    print("Time taken: {}".format(total_processing_time))
    print("FPS: {}".format(frame_sum/total_processing_time))

