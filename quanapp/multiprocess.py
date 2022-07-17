import cv2 as cv
import time
import subprocess as sp
import multiprocessing as mp
from os import remove
import dlib
from imutils import face_utils

def process_video():
    # Read video file
    cap = cv.VideoCapture(file_name)

    # get height, width and frame count of the video
    width, height = (
            int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        )
    fps = int(cap.get(cv.CAP_PROP_FPS))

    # Define the codec and create VideoWriter object
    fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv.VideoWriter()
    output_file_name = "output_single.mp4"
    out.open(output_file_name, fourcc, fps, (width, height), True)

    try:
        while cap.isOpened():
            _, image = cap.read()
            gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

            rects = detector(gray, 0)

            for (i, rect) in enumerate(rects):
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                
                for(x, y) in shape:
                    cv.circle(image, (x, y), 2, (0, 255, 0), -1)
            out.write(image)
            #cv.imshow("Output", image)
    except:
        # Release resources
        cap.release()
        out.release()
    # Release resources
    cap.release()
    out.release()

def single_process():
    print("Video processing using single process...")
    start_time = time.time()
    process_video()
    end_time = time.time()
    total_processing_time = end_time - start_time
    print("Time taken: {}".format(total_processing_time))
    print("FPS : {}".format(frame_count/total_processing_time))

def process_video_multiprocessing(group_number):
    # Read video file
    print(group_number, end=" ")
    cap = cv.VideoCapture(file_name)
    cap.set(cv.CAP_PROP_POS_FRAMES, frame_jump_unit * group_number)
    # get height, width and frame count of the video
    width, height = (
            int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        )
    no_of_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv.CAP_PROP_FPS))
    proc_frames = 0

    # Define the codec and create VideoWriter object
    fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv.VideoWriter()
    output_file_name = "output_multi.mp4"
    out.open("output_{}.mp4".format(group_number), fourcc, fps, (width, height), True)
    try:
        while proc_frames < frame_jump_unit:
            ret, image = cap.read()
            if not ret:
                print("no")
                break
            gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            rects = detector(gray, 0)
            for (i, rect) in enumerate(rects):
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                for(x, y) in shape:
                    cv.circle(image, (x, y), 2, (0, 255, 0), -1)
            out.write(image)
            #cv.imshow("Output", image)
            k = cv.waitKey(5) & 0xFF
            if k == 27:
                break
            proc_frames += 1
    except:
        # Release resources
        cap.release()
        out.release()

    # Release resources
    cap.release()
    out.release()

def combine_output_files(num_processes):
    # Create a list of output files and store the file names in a txt file
    print("in combine")
    list_of_output_files = ["output_{}.mp4".format(i) for i in range(num_processes)]
    with open("list_of_output_files.txt", "w") as f:
        for t in list_of_output_files:
            f.write("file {} \n".format(t))

    # use ffmpeg to combine the video output files
    ffmpeg_cmd = "ffmpeg -y -loglevel error -f concat -safe 0 -i list_of_output_files.txt -vcodec copy " + output_file_name
    sp.Popen(ffmpeg_cmd, shell=True).wait()

    # Remove the temperory output files
    for f in list_of_output_files:
        remove(f)
    remove("list_of_output_files.txt")

def multi_process():
    print("Video processing using {} processes...".format(num_processes))
    start_time = time.time()

    # Paralle the execution of a function across multiple input values
    print("0")
    p = mp.Pool
    print("1")
    with p(num_processes) as pool:
        pool.map(process_video_multiprocessing, range(num_processes))
    print("2")

    combine_output_files(num_processes)
    print("3")

    end_time = time.time()
    print("4")

    total_processing_time = end_time - start_time
    print("Time taken: {}".format(total_processing_time))
    print("FPS : {}".format(frame_count/total_processing_time))

def get_video_frame_details(file_name):
    cap = cv.VideoCapture(file_name)
    width, height = (
            int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        )
    no_of_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    return width, height, no_of_frames


p = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(p)

file_name = "video.mp4"
output_file_name = "output_single.mp4"
width, height, frame_count = get_video_frame_details(file_name)
single_process()

output_file_name = "output_multi.mp4"
width, height, frame_count = get_video_frame_details(file_name)
print("Video frame count = {}".format(frame_count))
print("Width = {}, Height = {}".format(width, height))
num_processes = 2
print("Number of CPU: " + str(num_processes))
frame_jump_unit =  frame_count// num_processes
##multi_process()



