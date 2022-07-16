from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify, Response
import multiprocessing
import random
from quanapp.camera import Camera1, Camera2

from quanapp import app, ENV
# from quanapp.model import Camera
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

def frameavg(lst):
    m = 0
    n = len(lst)
    for i in range(n):
        m+=lst[i]
    print("Avg:", format(m/n, ".5f"))

def gen_frames(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# datachange()

@app.route("/", methods = ['GET', 'POST'])
def dashboard():
    session['ENV'] = ENV
    alertctgra = [["Mar", "Apr", "May", "Jun", "Jul", "Aug"], [860,1140,1060,1060,1070,1110], [300,700,2000,5000,6000,4000], [1600,1700,1700,1900,2000,2700]]
    behaana = [["Mar", "Apr", "May", "Jun", "Jul", "Aug"], [860,1140,1060,1060,1070,1110], [1600,1700,1700,1900,2000,2700], [300,700,2000,5000,6000,4000]]
    sevedis = [["Low", "Medium", "High"], [50, 30, 20]]
    datachange()
    # alertctgra = [["Mar", "Apr", "May", "Jun", "Jul", "Aug"], [1060,1070,860,1140,1060,1110], [300,6000,700,2000,5000,4000], [1600,1700,1900,2000,1700,2700]]
    # behaana = [["Mar", "Apr", "May", "Jun", "Jul", "Aug"], [860,1140,1070,1110,1060,1060], [1600,1900,2000,2700,1700,1700], [2000,5000,6000,300,700,4000]]
    # sevedis = [["Low", "Medium", "High"], [20, 70, 10]]
    f = open("bases.txt", "r")
    dat = f.read()
    data = dat.split(",")
    if request.is_json:
        frameavg(Camera1.lst)
        frameavg(Camera2.lst)
        return jsonify({'tdyalertct':  data[0], 'sthighrsk':  data[1], 'sthighvio':  data[2], 'ppevio':  data[3], 'workhei':  data[4]})
    return render_template('dashboard.html', tdyalertct = data[0], sthighrsk = data[1], sthighvio = data[2], alertctgra = alertctgra, behaana = behaana, sevedis = sevedis, ppevio = data[3], workhei = data[4])

@app.route("/video_feed1", methods = ['GET', 'POST'])
def video_feed1():
    Camera1.set_video_source(0)
    return Response(gen_frames(Camera1(camera_type="opencv", device=0)), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/video_feed2", methods = ['GET', 'POST'])
def video_feed2():
    Camera2.set_video_source(2)
    return Response(gen_frames(Camera2(camera_type="opencv", device=2)), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/sitemap")
def sitemap():
    # Route to dynamically generate a sitemap of your website/application. lastmod and priority tags omitted on static pages. lastmod included on dynamic content such as blog posts.
    from flask import make_response, request, render_template
    import datetime
    from urllib.parse import urlparse
    host_components = urlparse(request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc
    # Static routes with static content
    urlstatic = []
    for rule in app.url_map.iter_rules():
        if not str(rule).startswith("/admin") and not str(rule).startswith("/user"):
            urlstatic.append(f"{host_base}{str(rule)}")
    urlstatic.sort()
    # Dynamic routes with dynamic content
    try:
        dynamic_urls = list()
        blog_posts = Post.objects(published = True)
        for post in blog_posts:
            url = {"loc": f"{host_base}/blog/{post.category.name}/{post.url}", "lastmod": post.date_published.strftime("%Y-%m-%dT%H:%M:%SZ")}
            dynamic_urls.append(url)
        xml_sitemap = render_template("sitemap.xml", urlstatic = urlstatic, dynamic_urls = dynamic_urls, host_base = host_base)
    except:
        xml_sitemap = render_template("sitemap.xml", urlstatic = urlstatic, host_base = host_base)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"
    return response

