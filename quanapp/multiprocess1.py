import cv2
import dlib
from imutils import face_utils
import dlib

from multiprocessing import Process, Queue

p = "quanapp/shape_predictor_68_face_landmarks.dat"
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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        for (i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            for(x, y) in shape:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        ret, buffer = cv2.imencode(".jpg", frame)
        image = buffer.tobytes()
        if self.output_queue.full():
            self.output_queue.get_nowait()
        self.output_queue.put(image)

    def run(self):
        while not self.stop:
            ret, frame = self.get_frame()
            if ret:
                self.canny_frame(frame)

def process_video(cam_no):
    def put_frame(frame):
        if Input_Queue.full():
            Input_Queue.get_nowait()
        Input_Queue.put(frame)

    def cap_read(cv2_cap):
        ret, frame = cv2_cap.read()
        if ret:
            put_frame(frame)

    process_list = []
    threadn = 8
    Input_Queue = Queue(maxsize = threadn+1)
    Output_Queue = Queue(maxsize = threadn+1)

    cap = cv2.VideoCapture(cam_no)

    for x in range(threadn-1):
        canny_process = Canny_Process(frame_queue = Input_Queue,output_queue = Output_Queue)
        canny_process.daemon = True
        canny_process.start()
        process_list.append(canny_process)

    # fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    # out = cv2.VideoWriter()
    # out.open('multi_vid1.mp4', fourcc, 25, (960, 540), True)
    # cv2.namedWindow('Threaded Video', cv2.WINDOW_NORMAL)
    # ch = cv2.waitKey(1)
    cap_read(cap)
    try:
        while True:
            # print("a", Input_Queue.qsize(), Output_Queue.qsize(), end=" ")
            if Input_Queue.empty():
                cap_read(cap)
            # print("b", Input_Queue.qsize(), Output_Queue.qsize(), end=" ")
            if Input_Queue.empty() and Output_Queue.empty():
                break
            if not Output_Queue.empty():
                frame = Output_Queue.get()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                # frame_sum = frame_sum + 1
                # out.write(result)
                # print(frame_sum, end=" ")
                # cv2.imshow('Threaded Video', result)
            # print("c", Input_Queue.qsize(), Output_Queue.qsize(), end="\n")
            # ch = cv2.waitKey(5)
    except:
        cap.release()
        # out.release()
    cap.release()
    # out.release()

# if __name__ == "__main__":
    # frame_sum = 0
    # threaded_mode = True
    # start_time = time.time()
    # process_video()
    # end_time = time.time()
    # total_processing_time = end_time - start_time
    # print("Time taken: {}".format(total_processing_time))
    # print("FPS: {}".format(frame_sum/total_processing_time))

