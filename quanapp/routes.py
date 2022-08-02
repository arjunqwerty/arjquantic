from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify, Response
import random
import cv2

from quanapp import app, ENV
from quanapp.multiprocess1 import process_video
## COMMON

sites = ["Warehouse", "AB Unit", "Stamping", "Entrance", "Phase 1"]
def datachange():
    with open("bases.txt", "w", newline="") as f:
        alct = str(random.randint(0, 100))
        rsk = random.choice(sites).upper()
        vio = random.choice(sites).upper()
        ppe = str(random.randint(0, 100))
        work = str(random.randint(0, 100))
        row = alct + "," +  rsk + "," + vio +  "," + ppe +  "," + work
        f.write(row)

def gen_frames(camera):
    cap = cv2.VideoCapture(camera)
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.release()
            cap = cv2.VideoCapture(camera)
            ret, frame = cap.read()
        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/", methods = ['GET', 'POST'])
def dashboard():
    session['ENV'] = ENV
    alertctgra = [["Mar", "Apr", "May", "Jun", "Jul", "Aug"], [860,1140,1060,1060,1070,1110], [300,700,2000,5000,6000,4000], [1600,1700,1700,1900,2000,2700]]
    behaana = [["Mar", "Apr", "May", "Jun", "Jul", "Aug"], [860,1140,1060,1060,1070,1110], [1600,1700,1700,1900,2000,2700], [300,700,2000,5000,6000,4000]]
    sevedis = [["Low", "Medium", "High"], [50, 30, 20]]
    datachange()
    f = open("bases.txt", "r")
    dat = f.read()
    data = dat.split(",")
    if request.is_json:
        return jsonify({'tdyalertct':  data[0], 'sthighrsk':  data[1], 'sthighvio':  data[2], 'ppevio':  data[3], 'workhei':  data[4]})
    return render_template('dashboard.html', tdyalertct = data[0], sthighrsk = data[1], sthighvio = data[2], alertctgra = alertctgra, behaana = behaana, sevedis = sevedis, ppevio = data[3], workhei = data[4])

@app.route("/cctv", methods = ['GET', 'POST'])
def cctv():
    # Change list index 1 for the text to be displayed near the preview
    # Change list index 2 to change the video and preview image file name
    # Change list index 3 to change the text shown below the 
    cam = [[0, "CCTV1", "activity", "Camera one is activity"],
    [1, "CCTV2", "fence", "Camera two is fence"],
    [2, "CCTV3", "construction_site", "Camera three is construction site"]]
    return render_template("cctv.html", cameras = cam)

@app.route("/video_feed1", methods = ['GET', 'POST'])
def video_feed1():
    return Response(process_video('rtsp://Quantic:Quantic@192.168.1.101:554/stream1'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/CCTV2", methods = ['GET', 'POST'])
def cctv2():
    return Response(gen_frames("activity.mp4"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/CCTV3", methods = ['GET', 'POST'])
def cctv3():
    return Response(gen_frames("fence.mp4"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/CCTV4", methods = ['GET', 'POST'])
def cctv4():
    return Response(gen_frames("construction_site.mp4"), mimetype='multipart/x-mixed-replace; boundary=frame')
