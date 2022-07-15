from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from functools import wraps
from passlib.hash import sha256_crypt as sa
import random
import smtplib
from email.mime.text import MIMEText

from zorgapp import app, db, ENV
from zorgapp.model import RegisterMnmg, CustomerDet, Appointments, Orders, PastOrders, StaffDet

# NORMAL DEFINITIONS

def username_predict(u, t):
    c = True
    while c:
        if not db.session.query(t).filter(t.username == u).count() == 0:
            x = random.randint(0, 6000)
            u += str(x)
            s = ". Try " + u
            c = False
    return s

def emailsend(to, mssg):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = '18cc8c2ea71e43'
    password = '27abc8c416d687'
    sender_email = 'zorg123546@gmail.com'
    message = MIMEText(mssg, 'html')
    message['Subject'] = 'Zorg'
    message['From'] = sender_email
    message['To'] = str(to)

    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender_email, to, message.as_string())

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('UNAUTHORISED, Please Login', 'danger')
            return redirect(url_for('home'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin' in session:
            return f(*args, **kwargs)
        else:
            flash('UNAUTHORISED', 'danger')
            return redirect(url_for('home'))
    return wrap

def is_not_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            sendurl = session['url']
            flash('UNAUTHORISED', 'danger')
            return redirect(url_for(sendurl))
        else:
            return f(*args, **kwargs)
    return wrap

# UNLOGGED
## COMMON

@app.route("/", methods = ['GET', 'POST'])
def home():
    if ENV == "dev":
        return redirect(url_for("index"))
    return render_template('preloader.html')

@app.route("/index", methods = ['GET', 'POST'])
def index():
    session['ENV'] = ENV
    return render_template('index.html')

@app.route("/feedback", methods = ['GET', 'POST'])
def feedback():
    if request.method == "POST":
        mail = request.form['mailid']
        rating = request.form['rating']
        feedback = request.form['feedback']
        try:
            feed = rating + "\nFeedback Submitted:\n" + feedback
            emailsend(mail, feed)
            flash('Your response has been recorded', 'success')
            if ENV == "dev":
                return redirect(url_for('index'))
            else:
                return redirect(url_for('home'))
        except:
            flash('Please enter all the details asked for', 'danger')
            return render_template('feedback.html')
        return render_template('feedback.html')
    return render_template('feedback.html')

@app.route("/route", methods = ['GET', 'POST'])
def route():
    return render_template('route.html')

@app.route("/extra", methods = ['GET', 'POST'])
def extra():
    return render_template('index2.html')

@app.route("/extra2", methods = ['GET', 'POST'])
def extra2():
    alldata = db.session.query(CustomerDet).all()
    return render_template('tarun2.html', alldata = alldata)

@app.route("/extra3", methods = ['GET', 'POST'])
def extra3():
    return render_template('tarun3.html')

@app.route("/game", methods = ["GET", "POST"])
def game():
    if request.method == "POST":
        f = open("movieslist.txt", "r")
        movies = f.readlines()
        n = random.randrange(0, len(movies))
        chosenmovie = movies[n]
        return render_template("game.html", movie = chosenmovie)
    return render_template("game.html")

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

@app.route("/register", methods = ['GET', 'POST'])#to be changed to show a html which shows both hospital and customer
def register():
    return render_template("index.html")

@app.route("/login", methods=['GET','POST'])#to be changed to show a html which shows both hospital and customer
def login():
    return render_template("index.html")

##HOSPITAL

@app.route("/register/hospital", methods = ['GET', 'POST'])
def registerhospital():
    if request.method == 'POST':
        namehptl = request.form['namehptl']
        username = request.form['username']
        password = sa.hash(request.form['password'])
        pincode = request.form['pincode']
        address = request.form['address']
        if db.session.query(RegisterMnmg).filter(RegisterMnmg.username == username).count() == 0:
            data = RegisterMnmg(namehptl, username, password, pincode, address)
            db.session.add(data)
            db.session.commit()
            flash('you are now registered', 'success')
            return redirect(url_for('loginhospital'))
        else:
            flash("Username already exists" + username_predict(username, RegisterMnmg), 'danger')
    return render_template('remnmg.html')

@app.route("/login/hospital", methods = ['GET', 'POST'])
def loginhospital():
    if request.method == 'POST':
        usermnmg = request.form['username']
        password_candidate = request.form['password']
        user = db.session.query(RegisterMnmg).filter(RegisterMnmg.username == usermnmg).first()
        db.session.commit()
        if user is None:
            flash('No such username exists', 'danger')
            return render_template('lomnmg.html')
        else:
            if sa.verify(password_candidate, user.password):
                session['logged_in'] = True
                session['username'] = usermnmg
                session['name'] = user.namehptl
                session['type'] = 'H'
                session['pincode'] = user.pincode
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboardmnmg'))
            else:
                flash('Incorrect password', 'danger')
                return render_template('lomnmg.html')
    else:
        return render_template('lomnmg.html')

##CUSTOMER

@app.route("/register/customer", methods = ['GET', 'POST'])
def registercust():
    if request.method == 'POST':
        namecust = request.form['namecust']
        username = request.form['username']
        password = sa.hash(request.form['password'])
        gmail_id = request.form['gmail_id']
        aadhar = request.form['aadhar']
        address = ''
        pincode = ''
        age = ''
        gender = ''
        prevmedrcrds = ''
        if db.session.query(CustomerDet).filter(CustomerDet.username == username).count() == 0:
            data = CustomerDet(namecust, username, password, pincode, address, gmail_id, aadhar, age, gender, prevmedrcrds)
            db.session.add(data)
            db.session.commit()
            flash('you are now registered', 'success')
            return redirect(url_for('logincustomer'))
        else:
            flash("Username already exists" + username_predict(username, CustomerDet), 'danger')
    return render_template('recust.html')

@app.route("/login/customer", methods = ['GET', 'POST'])
def logincustomer():
    if request.method == 'POST':
        usercust = request.form['username']
        password_candidate = request.form['password']
        user = db.session.query(CustomerDet).filter(CustomerDet.username == usercust).first()
        db.session.commit()
        if user is None:
            flash('No such username exists', 'danger')
            return render_template('locust.html')
        else:
            if sa.verify(password_candidate, user.password):
                session['logged_in'] = True
                session['username'] = usercust
                session['type'] = 'C'
                session['name'] = user.namecust
                session['pincode'] = user.pincode
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboardcust'))
            else:
                flash('Incorrect password', 'danger')
                return render_template('locust.html')
    else:
        return render_template('locust.html')

#LOGGED IN

##COMMON

@app.route("/addappoint")
@is_logged_in
def appoint():
    session['problem'] = ""
    session['specs'] = ""
    session['hospname'] = ""
    session['docname'] = ""
    session['datetime'] = ""
    if session['type'] == "C":
        return redirect(url_for('addappointmentcust'))
    elif session['type'] == "H":
        session['patname'] = ""
        session['patusername'] = ""
        return redirect(url_for('addappointmenthosp'))

## HOSPITAL

@app.route("/hospital")
@is_logged_in
def dashboardmnmg():
    username = session['username']
    return render_template('dashboardmnmg.html', emernum = db.session.query(Orders).filter(Orders.hptl_username_in_vicinity == username).count(), aptnum = db.session.query(Appointments).filter(Appointments.HospName == username).count())

@app.route("/hospital/register/customer", methods = ['GET', 'POST'])
@is_logged_in
def registercustmnmg():
    session['url'] = 'registercustmnmg'
    if request.method == 'POST':
        namecust = request.form['namecust']
        username = request.form['username']
        password = sa.hash(request.form['password'])
        gmail_id = request.form['gmail_id']
        aadhar = request.form['aadhar']
        age = request.form['age']
        gender = request.form['gender']
        prevmedrcrds = request.form['prevmedrcrds']
        address = request.form['address']
        pincode = request.form['pincode']
        if db.session.query(CustomerDet).filter(CustomerDet.username == username).count() == 0:
            data = CustomerDet(namecust, username, password, pincode, address, gmail_id, aadhar, age, gender, prevmedrcrds)
            db.session.add(data)
            db.session.commit()
            flash('Registered', 'success')
            return redirect(url_for('dashboardmnmg'))
        else:
            flash("Username already exists" + username_predict(username, CustomerDet), 'danger')
    return render_template('recustmnmg.html')

@app.route("/hospital/emergency", methods = ['GET', 'POST'])
@is_logged_in
def emergency():
    session['url'] = 'emergency'
    username = session['username']
    help = db.session.query(Orders).filter(Orders.hptl_username_in_vicinity == username).first()
    db.session.commit()
    if help is None:
        flash("You have no one to save", "success")
        return render_template('emergency.html')
    else:
        return render_template('emergency.html', profile = db.session.query(Orders).filter(Orders.hptl_username_in_vicinity == username).order_by(Orders.number.asc()).all())
    return render_template('emergency.html')

@app.route("/hospital/emergency/accepted/<username>")
@is_logged_in
def accepted(username):
    if db.session.query(Orders).filter(Orders.username_cust == username).count() > 0:
        acc_or_dec = "a"
        name_of_hptl_result = session['name']
        message = f"<p>{name_of_hptl_result} has accepted to help you. They will arrive to your place soon.</p>"
        user = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
        gmail_id = user.gmail_id
        try:
            emailsend(gmail_id, message)
        except:
            flash('The person had registered with an invalid email. Could not deliver the message.', 'danger')
        user_order = db.session.query(Orders).filter(Orders.username_cust == username).first()
        data = PastOrders(name_of_hptl_result, user_order.username_cust, user_order.type, user_order.address, user_order.namecust, user_order.aadhar, user_order.age, user_order.gender, user_order.prevmedrcrds)
        db.session.add(data)
        edhavudhu = db.session.query(Orders).filter(Orders.username_cust == username).delete()
        db.session.commit()
        flash('You have accepted to save ' + user.namecust, 'success')
        return redirect(url_for('dashboardmnmg'))
    return render_template('dashboardmnmg.html')

@app.route("/hospital/emergency/declined/<username>")
@is_logged_in
def declined(username):
    if db.session.query(Orders).filter(Orders.username_cust == username).count() > 0:
        acc_or_dec = "d"
        name_of_hptl_result = session['username']
        message = f"<p>{name_of_hptl_result} has declined to help you. We are sorry.</p>"
        user = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
        gmail_id = user.gmail_id
        try:
            emailsend(gmail_id, message)
        except:
            flash('The person had registered with an invalid email. Could not deliver the message.', 'danger')
        user_order = db.session.query(Orders).filter(Orders.username_cust == username, Orders.hptl_username_in_vicinity == name_of_hptl_result).first()
        db.session.delete(user_order)
        db.session.commit()
        flash('You have declined to save ' + user.namecust, 'danger')
        return redirect(url_for('dashboardmnmg'))
    return render_template('dashboardmnmg.html')

@app.route("/hospital/emergency/history")
@is_logged_in
def patienthistory():
    session['url'] = 'patienthistory'
    username = session['name']
    help = db.session.query(PastOrders).filter(PastOrders.name_of_hptl_accepting_responsibilty == username).first()
    db.session.commit()
    if help is None:
        flash("You have not saved anyone yet", "danger")
        return render_template('patienthistory.html', profile = db.session.query(PastOrders).filter(PastOrders.name_of_hptl_accepting_responsibilty == username).order_by(PastOrders.number.asc()).all())
    else:
        return render_template('patienthistory.html', profile = db.session.query(PastOrders).filter(PastOrders.name_of_hptl_accepting_responsibilty == username).order_by(PastOrders.number.asc()).all())
    return render_template('patienthistory.html')

@app.route("/hospital/staff", methods = ['GET', 'POST'])
@is_logged_in
def hosdetails():
    session['url'] = 'hosdetails'
    username = session['username']
    return render_template('doctors.html', docdata = db.session.query(StaffDet).filter(StaffDet.hospitalid == username).order_by(StaffDet.docid.asc()).all())

@app.route("/hospital/staff/profile", methods = ['GET', 'POST'])#to be changed to showing a specific persons profile
@is_logged_in
def staffprofile():
    session['url'] = 'hosdetails'
    username = session['username']
    return render_template("doctors.html", docdata = db.session.query(StaffDet).filter(StaffDet.hospitalid == username).order_by(StaffDet.docid.asc()).all())

@app.route("/hospital/staff/profile/add", methods = ['GET', 'POST'])
@is_logged_in
def addprofilehos():
    session['url'] = 'hosdetails'
    username = session['username']
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        salary = request.form['salary']
        spec = request.form['spec']
        hospitalid = username
        if db.session.query(StaffDet).filter(StaffDet.name == name).count() != 0:
            userdata = db.session.query(StaffDet).filter(StaffDet.name == name).first()
            if userdata.age == age and userdata.gender == gender and userdata.salary == salary and userdata.spec == spec and userdata.hospitalid == hospitalid:
                flash('Worker already exists', 'danger')
                return redirect(url_for('hosdetails'))
        else:
            data = StaffDet(name, age, gender, salary, spec, hospitalid)
            db.session.add(data)
            db.session.commit()
            flash('Profile Created', 'success')
            return redirect(url_for('hosdetails'))
    return render_template('addprofilehos.html')

@app.route("/hospital/staff/profile/edit/<docid>", methods = ['GET', 'POST'])
@is_logged_in
def editprofilehos(docid):
    session['url'] = 'hosdetails'
    user = db.session.query(StaffDet).filter(StaffDet.docid == docid).first()
    db.session.commit()
    if request.method == 'POST':
        name = request.form['name']
        if name != '':
            user.name = name
        age = request.form['age']
        if age != '':
            user.age = age
        gender = request.form['gender']
        if gender != '':
            user.gender = gender
        salary = request.form['salary']
        if salary != '':
            user.salary = salary
        spec = request.form['spec']
        if spec != '':
            user.spec = spec
        db.session.commit()
        flash('Profile Updated', 'success')
        return redirect(url_for('hosdetails'))
    return render_template('editprofilehos.html', profile = db.session.query(StaffDet).filter(StaffDet.docid == docid).order_by(StaffDet.docid.asc()).all())

@app.route("/hospital/staff/profile/delete/<docid>", methods = ['GET', 'POST'])
@is_logged_in
def deletedoc(docid):
    data = db.session.query(StaffDet).filter(StaffDet.docid == docid).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('hosdetails'))

@app.route("/hospital/appointment")
@is_logged_in
def appointmenthosp():
    session['url'] = 'appointmenthosp'
    username = session['username']
    return render_template('appointmenthosp.html', apt = db.session.query(Appointments).filter(Appointments.HospName == username).order_by(Appointments.id.asc()).all())

@app.route("/hospital/appointment/add", methods = ['GET', 'POST'])
@is_logged_in
def addappointmenthosp():
    session['url'] = 'appointmenthosp'
    PatName = session['patname']
    PatUsername = session['patusername']
    problem = session['problem']
    specialisation = session['specs']
    DocName = session['docname']
    datetime = session['datetime']
    username = session['username']
    if request.method == 'POST':
        if PatUsername == "":
            PatUsername = request.form['patusername']
            patientinfo = db.session.query(CustomerDet).filter(CustomerDet.username == PatUsername).first()
            PatName = patientinfo.namecust
            session['patusername'] = PatUsername
            session['patname'] = PatName
            return redirect(url_for('addappointmenthosp'))
        else:
            if specialisation == "":
                problem = request.form['problem']
                specialisation = request.form['specialisation']
                session['problem'] = problem
                session['specs'] = specialisation
                return redirect(url_for('addappointmenthosp'))
            else:
                if DocName == "":
                    DocName = request.form['doctor']
                    session['docname'] = DocName
                    return redirect(url_for('addappointmenthosp'))
                else:
                    if datetime == "":
                        datetime = request.form['date']
                        n = datetime.find("T")
                        date = datetime[:n:]
                        time = datetime[n + 1::]
                        duplicate = db.session.query(Appointments).filter(Appointments.DocName == DocName, Appointments.date == date, Appointments.time == time).order_by(Appointments.id.asc()).all()
                        if duplicate == []:
                            status = "Accepted"
                            data = Appointments(PatName, PatUsername, problem, specialisation, DocName, username, date, time, status)
                            db.session.add(data)
                            db.session.commit()
                            flash("Appointment fixed", "success")
                            return redirect(url_for('appointmenthosp'))
                        else:
                            flash("The Doctor is busy at that time. Please pick another time", "danger")
                            return redirect(url_for('addappointmenthosp'))
    if PatUsername == "":
        return render_template('addappointmenthosp.html', patuser = PatUsername, pat = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all(), prob = problem, specs = db.session.query(StaffDet).filter(StaffDet.hospitalid == username).distinct(StaffDet.spec).all(), spec = specialisation, doc = DocName)
    else:
        if specialisation == "":
            return render_template('addappointmenthosp.html', patuser = PatUsername, pat = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all(), prob = problem, specs = db.session.query(StaffDet).filter(StaffDet.hospitalid == username).distinct(StaffDet.spec).all(), spec = specialisation, doc = DocName)
        else:
            if DocName == "":
                return render_template('addappointmenthosp.html', patuser = PatUsername, pat = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all(), prob = problem, specs = db.session.query(StaffDet).filter(StaffDet.hospitalid == username).distinct(StaffDet.spec).all(), spec = specialisation, hosps = db.session.query(StaffDet).filter(StaffDet.spec == specialisation).order_by(StaffDet.docid.asc()).all(), doc = DocName)
            else:
                return render_template('addappointmenthosp.html', patuser = PatUsername, pat = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all(), prob = problem, specs = db.session.query(StaffDet).filter(StaffDet.hospitalid == username).distinct(StaffDet.spec).all(), spec = specialisation, hosps = db.session.query(StaffDet).filter(StaffDet.spec == specialisation, StaffDet.hospitalid == username).order_by(StaffDet.docid.asc()).all(), doc = DocName)

@app.route("/hospital/appointment/accept/<num>", methods = ['GET', 'POST'])
@is_logged_in
def aptaccept(num):
    appoint = db.session.query(Appointments).filter(Appointments.id == num).first()
    specreq = appoint.Specialisation
    hospname = appoint.HospName
    if request.method == "POST":
        docchosen = request.form['doc']
        appoint.DocName = docchosen
        appoint.status = "Accepted"
        db.session.commit()
        return redirect(url_for('appointmenthosp'))
    return render_template('aptaccept.html', number = num, apt = db.session.query(StaffDet).filter(StaffDet.hospitalid == hospname, StaffDet.spec == specreq).order_by(StaffDet.docid.asc()).all())

@app.route("/hospital/appointment/decline/<num>", methods = ['GET', 'POST'])
@is_logged_in
def aptdecline(num):
    appointment = db.session.query(Appointments).filter(Appointments.id == num).first()
    appointment.status = "Declined"
    db.session.commit()
    return redirect(url_for('appointmenthosp'))

# CUSTOMER

@app.route("/customer", methods = ['GET', 'POST'])
@is_logged_in
def dashboardcust():
    session['url'] = 'dashboardcust'
    username = session['username']
    custdata = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    db.session.commit()
    if custdata.age == '' or custdata.gender == '' or custdata.prevmedrcrds == '' or custdata.address == '' or custdata.pincode == '':
        flash("Please fill these details", "danger")
        return redirect(url_for('addprofile'))
    else:
        return render_template('dashboardcust.html', custdata = db.session.query(CustomerDet).filter(CustomerDet.username == username).order_by(CustomerDet.custid.asc()).all())
    return render_template('dashboardcust.html')

@app.route("/customer/profile", methods = ['GET', 'POST'])
@is_logged_in
def customerprofile():
    return render_template("dashboardcust.html")

@app.route("/customer/profile/add", methods = ['GET', 'POST'])
@is_logged_in
def addprofile():
    session['url'] = 'dashboardcust'
    username = session['username']
    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        prevmedrcrds = request.form['prevmedrcrds']
        address = request.form['address']
        pincode = request.form['pincode']
        if db.session.query(CustomerDet).filter(CustomerDet.username == username).count() == 1:
            update = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
            update.age = age
            update.gender = gender
            update.prevmedrcrds = prevmedrcrds
            update.address = address
            update.pincode = pincode
            db.session.commit()
            flash('Profile Created', 'success')
            return redirect(url_for('dashboardcust'))
        else:
            return redirect(url_for('editprofile'))
    return render_template('addprofile.html')

@app.route("/customer/profile/edit", methods = ['GET', 'POST'])
@is_logged_in
def editprofile():
    session['url'] = 'dashboardcust'
    username = session['username']
    user = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    db.session.commit()
    if request.method == 'POST':
        age = request.form['age']
        if age != '':
            user.age = age
        prevmedrcrds = request.form['prevmedrcrds']
        if prevmedrcrds != '':
            user.prevmedrcrds = prevmedrcrds
        address = request.form['address']
        if address != '':
            user.address = address
        pincode = request.form['pincode']
        if pincode != '':
            user.pincode = pincode
        gmail_id = request.form['gmail_id']
        if gmail_id != '':
            user.gmail_id = gmail_id
        db.session.commit()
        flash('Profile Updated', 'success')
        return redirect(url_for('dashboardcust'))
    return render_template('editprofile.html', profile = db.session.query(CustomerDet).filter(CustomerDet.username == username).order_by(CustomerDet.custid.asc()).all())

@app.route("/customer/appointment")
@is_logged_in
def appointmentcust():
    session['url'] = "appointmentcust"
    username = session['username']
    return render_template('appointmentcust.html', apt = db.session.query(Appointments).filter(Appointments.PatUsername == username).order_by(Appointments.id.asc()).all())

@app.route("/customer/appointment/add", methods = ['GET', 'POST'])
@is_logged_in
def addappointmentcust():
    session['url'] = "appointmentcust"
    problem = session['problem']
    specialisation = session['specs']
    HospName = session['hospname']
    DocName = session['docname']
    datetime = session['datetime']
    username = session['username']
    aptdata = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    PatName = aptdata.namecust
    PatUsername = aptdata.username
    if request.method == 'POST':
        if specialisation == "":
            problem = request.form['problem']
            specialisation = request.form['specialisation']
            session['problem'] = problem
            session['specs'] = specialisation
            return redirect(url_for('addappointmentcust'))
        else:
            if HospName == "":
                HospName = request.form['hospital']
                session['hospname'] = HospName
                return redirect(url_for('addappointmentcust'))
            else:
                if datetime == "":
                    datetime = request.form['date']
                    n = datetime.find("T")
                    date = datetime[:n:]
                    time = datetime[n + 1::]
                    status = ""
                    data = Appointments(PatName, PatUsername, problem, specialisation, DocName, HospName, date, time, status)
                    db.session.add(data)
                    db.session.commit()
                    flash("Appointment fixed", "success")
                    return redirect(url_for('appointmentcust'))
    if specialisation == "":
        return render_template('addappointmentcust.html', prob = problem, specs = db.session.query(StaffDet).distinct(StaffDet.spec).all(), spec = specialisation, hosp = HospName)
    else:
        if HospName == "":
            return render_template('addappointmentcust.html', prob = problem, specs = db.session.query(StaffDet).distinct(StaffDet.spec).all(), spec = specialisation, hosps = db.session.query(StaffDet).distinct(StaffDet.hospitalid).all(), hosp = HospName)
        else:
            return render_template('addappointmentcust.html', prob = problem, specs = db.session.query(StaffDet).distinct(StaffDet.spec).all(), spec = specialisation, hosps = db.session.query(StaffDet).filter(StaffDet.hospitalid == HospName).distinct(StaffDet.hospitalid).all(), hosp = HospName)

@app.route("/customer/appointment/delete/<number>", methods = ['GET', 'POST'])
@is_logged_in
def deleteappoint(number):
    appointdele = db.session.query(Appointments).filter(Appointments.id == number).first()
    db.session.delete(appointdele)
    db.session.commit()
    return redirect(url_for('appointmentcust'))

@app.route("/customer/emergency")#to be changed to a html where we can select all 3 emergencies
@is_logged_in
def emergencycust():
    return render_template("dashboardcust.html")

@app.route("/customer/emergency/accident")
@is_logged_in
def accident():
    session['url'] = 'dashboardcust'
    username = session['username']
    list_of_hosp_to_send_message = []
    profile = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    custpincode = profile.pincode
    hospital_to_send_request = db.session.query(RegisterMnmg).filter_by(pincode = custpincode).order_by(RegisterMnmg.username.asc()).all()
    db.session.commit()
    for hospital in hospital_to_send_request:
        list_of_hosp_to_send_message.append(hospital.username)
    if profile is not None:
        if list_of_hosp_to_send_message != []:
            if db.session.query(Orders).filter(Orders.username_cust == username).count() == 0:
                type = 'Accident'
                for hptl_username_in_vicinity in list_of_hosp_to_send_message:
                    data = Orders(hptl_username_in_vicinity, username, type, profile.address, profile.namecust, profile.aadhar, profile.age, profile.gender, profile.prevmedrcrds)
                    db.session.add(data)
                    db.session.commit()
                return render_template('request_sent.html')
            else:
                flash('you have already sent a request, kindly wait till it is processed', 'danger')
                return render_template('request_sent.html')
        else:
            return render_template('sorry.html')
    else:
        flash('Please fill in your details so that we can send it to the hospitals', 'danger')
        return redirect(url_for('addprofile'))
    return render_template('request_sent.html')

@app.route("/customer/emergency/heartattack")
@is_logged_in
def heartattack():
    session['url'] = 'dashboardcust'
    username = session['username']
    list_of_hosp_to_send_message = []
    profile = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    hospital_to_send_request = db.session.query(RegisterMnmg).filter_by(pincode = profile.pincode).order_by(RegisterMnmg.username.asc()).all()
    db.session.commit()
    for hospital in hospital_to_send_request:
        list_of_hosp_to_send_message.append(hospital.username)
    if profile is not None:
        if list_of_hosp_to_send_message != []:
            if db.session.query(Orders).filter(Orders.username_cust == username).count() == 0:
                type = 'Heart Attack'
                for hptl_username_in_vicinity in list_of_hosp_to_send_message:
                    data = Orders(hptl_username_in_vicinity, username, type, profile.address, profile.namecust, profile.aadhar, profile.age, profile.gender, profile.prevmedrcrds)
                    db.session.add(data)
                    db.session.commit()
                return render_template('request_sent.html')
            else:
                flash('you have already sent a request, kindly wait till it is processed', 'danger')
                return render_template('request_sent.html')
        else:
            return render_template('sorry.html')
    else:
        flash('Please fill in your details so that we can send it to the hospitals', 'danger')
        return redirect(url_for('addprofile'))
    return render_template('request_sent.html')

@app.route("/customer/emergency/otherailments")
@is_logged_in
def otherailments():
    session['url'] = 'dashboardcust'
    username = session['username']
    list_of_hosp_to_send_message = []
    profile = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    hospital_to_send_request = db.session.query(RegisterMnmg).filter_by(pincode = profile.pincode).order_by(RegisterMnmg.username.asc()).all()
    db.session.commit()
    for hospital in hospital_to_send_request:
        list_of_hosp_to_send_message.append(hospital.username)
    if profile is not None:
        if list_of_hosp_to_send_message != []:
            if db.session.query(Orders).filter(Orders.username_cust == username).count() == 0:
                type = 'Other Ailments'
                for hptl_username_in_vicinity in list_of_hosp_to_send_message:
                    data = Orders(hptl_username_in_vicinity, username, type, profile.address, profile.namecust, profile.aadhar, profile.age, profile.gender, profile.prevmedrcrds)
                    db.session.add(data)
                    db.session.commit()
                return render_template('request_sent.html')
            else:
                flash('you have already sent a request, kindly wait till it is processed', 'danger')
                return render_template('request_sent.html')
        else:
            return render_template('sorry.html')
    else:
        flash('please fill in your details so that we can send it to the hospitals', 'danger')
        return redirect(url_for('addprofile'))
    return render_template('request_sent.html')

@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('home'))

# ADMIN PROCESS

@app.route("/admin/login", methods = ['GET', 'POST'])
@is_not_admin
def loginadmin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'Administrator':
            if password == 'Administrator':
                session['admin'] = True
                return redirect(url_for('admindash'))
            else:
                flash('UNAUTHORISED', 'Danger')
                return redirect(url_for('home'))
        else:
            flash('UNAUTHORISED', 'Danger')
            return redirect(url_for('home'))
    return render_template('loginadmin.html')

@app.route("/admin/dashboard", methods = ['GET', 'POST'])
@is_admin
def admindash():
    return render_template('admindash.html')

@app.route("/admin/table/display/<number>", methods = ['GET', 'POST'])
@is_admin
def displaytables(number):
    session['number'] = number
    if number == "All":
        return render_template('displaytables.html', registermnmg = db.session.query(RegisterMnmg).order_by(RegisterMnmg.username.asc()).all(), customerdet = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all(), orders = db.session.query(Orders).order_by(Orders.number.asc()).all(), pastorders = db.session.query(PastOrders).order_by(PastOrders.number.asc()).all(), staffdet = db.session.query(StaffDet).order_by(StaffDet.docid.asc()).all(), appoints = db.session.query(Appointments).order_by(Appointments.id.asc()).all())
    elif number == '1':
        return render_template('displaytables.html', registermnmg = db.session.query(RegisterMnmg).order_by(RegisterMnmg.username.asc()).all())
    elif number == '2':
        return render_template('displaytables.html', customerdet = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all())
    elif number == '3':
        return render_template('displaytables.html', orders = db.session.query(Orders).order_by(Orders.number.asc()).all())
    elif number == '4':
        return render_template('displaytables.html', pastorders = db.session.query(PastOrders).order_by(PastOrders.number.asc()).all())
    elif number == '5':
        return render_template('displaytables.html', staffdet = db.session.query(StaffDet).order_by(StaffDet.docid.asc()).all())
    elif number == '6':
        return render_template('displaytables.html', appoints = db.session.query(Appointments).order_by(Appointments.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for('home'))
    return render_template('displaytables.html')

hospital_list = [['Newlife Hospital', 'newlife123', 'newlife123', '123456', 'Chennai'], ['Medwin Cares Hospital', 'medwin123', 'medwin123', '321654', 'Vellore'], ['Red Star Hospital', 'redstar123', 'redstar123', '123456', 'Madurai'], ['Angel Care Hospital', 'angel123', 'angel123', '321654', 'Trichy']]
customer_list = [['1', 'James', 'james123', 'james123', '123456', 'Chennai', 'james@mail.com', '123456789123456', '25', 'M', 'Fever'], ['2', 'Mary', 'mary123', 'mary123', '321654', 'Vellore', 'mary@mail.com', '321654987321654', '27', 'F', 'Cholera'], ['3', 'John', 'john123', 'john123', '123456', 'Madurai', 'john@mail.com', '147258369147258', '34', 'M', 'Diahorea'], ['4', 'Julie', 'julie123', 'julie123', '321654', 'Trichy', 'julie@mail.com', '369258147369258', '29', 'F', 'Jaundice']]
staff_list = [['David', '34', 'M', '50000', 'Cardiology', 'newlife123'], ['Lisa', '30', 'F', '60000', 'Oncolgy', 'newlife123'], ['Charles', '47', 'M', '55000', 'Neurology', 'newlife123'], ['Karen', '43', 'F', '75000', 'Urology', 'newlife123'], ['Thomas', '44', 'M', '65000', 'Gastroenterology', 'medwin123'], ['Emily', '41', 'F', '60000', 'Gynaecology', 'medwin123'], ['Donald', '39', 'M', '70000', 'Endocrinology', 'medwin123'], ['Nancy', '45', 'F', '80000', 'Nephrology', 'medwin123'], ['Gary', '49', 'M', '90000', 'Neurology', 'medwin123'], ['Amy', '38', 'F', '85000', 'Physiotherapy', 'redstar123'], ['Nick', '31', 'M', '80000', 'Psychiatry', 'redstar123'], ['Carol', '36', 'F', '75000', 'Urology', 'redstar123'], ['Ryan', '40', 'M', '70000', 'Ophthalmology', 'angel123'], ['Helen', '42', 'F', '65000', 'Neonatology', 'angel123'], ['Justin', '44', 'M', '80000', 'Anaesthesia', 'angel123'], ['Emma', '48', 'F', '75000', 'ENT', 'angel123'], ['Gary', '51', 'M', '65000', 'Dermatology', 'angel123']]

@app.route("/admin/table/default/<number>", methods = ['GET', 'POST'])
@is_admin
def defaultable(number):
    session['number'] = number
    if number == "All":
        db.session.query(RegisterMnmg).delete()
        db.session.query(CustomerDet).delete()
        db.session.query(Orders).delete()
        db.session.query(PastOrders).delete()
        db.session.query(StaffDet).delete()
        db.session.query(Appointments).delete()
        addreghospital(hospital_list)
        addregcustomer(customer_list)
        addhospitaldet(staff_list)
        db.session.commit()
    elif number == '1':
        db.session.query(RegisterMnmg).delete()
        addreghospital(hospital_list)
        db.session.commit()
    elif number == '2':
        db.session.query(CustomerDet).delete()
        addregcustomer(customer_list)
        db.session.commit()
    elif number == '3':
        db.session.query(Orders).delete()
        db.session.commit()
    elif number == '4':
        db.session.query(PastOrders).delete()
        db.session.commit()
    elif number == '5':
        db.session.query(StaffDet).delete()
        addhospitaldet(staff_list)
        db.session.commit()
    elif number == '6':
        db.session.query(Appointments).delete()
        db.session.commit()
    else:
        flash("No such table exists", "danger")
        return redirect(url_for('admindash'))
    return redirect(url_for('admindash'))

def addreghospital(hospital_list):
    if len(hospital_list) == 0:
        chumma = 0
    else:
        row = hospital_list[0]
        data = RegisterMnmg(row[0], row[1], sa.hash(row[2]), row[3], row[4])
        db.session.add(data)
        db.session.commit()
        list1 = []
        for i in range(len(hospital_list)):
            if i > 0:
                list1.append(hospital_list[i])
        addreghospital(list1)

def addregcustomer(customer_list):
    if len(customer_list) == 0:
        chumma = 0
    else:
        row = customer_list[0]
        data = CustomerDet(row[1], row[2], sa.hash(row[3]), row[4], row[5], row[6], row[7], row[8], row[9], row[10])
        db.session.add(data)
        db.session.commit()
        list2 = []
        for j in range(len(customer_list)):
            if j > 0:
                list2.append(customer_list[j])
        addregcustomer(list2)

def addhospitaldet(staff_list):
    if len(staff_list) == 0:
        chumma = 0
    else:
        row = staff_list[0]
        data = StaffDet(row[0], row[1], row[2], row[3], row[4], row[5])
        db.session.add(data)
        db.session.commit()
        list3 = []
        for k in range(len(staff_list)):
            if k > 0:
                list3.append(staff_list[k])
        addhospitaldet(list3)

@app.route("/admin/table/delete/<number>", methods = ['GET', 'POST'])
@is_admin
def deletetables(number):
    if number == "All":
        db.session.query(RegisterMnmg).delete()
        db.session.query(CustomerDet).delete()
        db.session.query(Orders).delete()
        db.session.query(PastOrders).delete()
        db.session.query(StaffDet).delete()
        db.session.query(Appointments).delete()
        db.session.commit()
    elif number == '1':
        db.session.query(RegisterMnmg).delete()
        db.session.commit()
    elif number == '2':
        db.session.query(CustomerDet).delete()
        db.session.commit()
    elif number == '3':
        db.session.query(Orders).delete()
        db.session.commit()
    elif number == '4':
        db.session.query(PastOrders).delete()
        db.session.commit()
    elif number == '5':
        db.session.query(StaffDet).delete()
        db.session.commit()
    elif number == '6':
        db.session.query(Appointments).delete()
        db.session.commit()
    else:
        flash("No such table exists", "danger")
        return redirect(url_for('admindash'))
    return redirect(url_for('admindash'))

@app.route("/admin/table/delete/row/<number>", methods = ['GET', 'POST'])
@is_admin
def deletetablerow(number):
    session['number'] = number
    if number == "All":
        return render_template('deletetablerow.html', registermnmg = db.session.query(RegisterMnmg).order_by(RegisterMnmg.username.asc()).all(), customerdet = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all(), orders = db.session.query(Orders).order_by(Orders.number.asc()).all(), pastorders = db.session.query(PastOrders).order_by(PastOrders.number.asc()).all(), staffdet = db.session.query(StaffDet).order_by(StaffDet.docid.asc()).all(), appoints = db.session.query(Appointments).order_by(Appointments.id.asc()).all())
    elif number == '1':
        return render_template('deletetablerow.html', registermnmg = db.session.query(RegisterMnmg).order_by(RegisterMnmg.username.asc()).all())
    elif number == '2':
        return render_template('deletetablerow.html', customerdet = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all())
    elif number == '3':
        return render_template('deletetablerow.html', orders = db.session.query(Orders).order_by(Orders.number.asc()).all())
    elif number == '4':
        return render_template('deletetablerow.html', pastorders = db.session.query(PastOrders).order_by(PastOrders.number.asc()).all())
    elif number == '5':
        return render_template('deletetablerow.html', staffdet = db.session.query(StaffDet).order_by(StaffDet.docid.asc()).all())
    elif number == '6':
        return render_template('deletetablerow.html', appoints = db.session.query(Appointments).order_by(Appointments.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for('admindash'))
    return render_template("deletetablerow.html")

@app.route("/admin/delete/row/<chumma>", methods = ['GET', 'POST'])
@is_admin
def deleterow(chumma):
    number = session['number']
    session['chumma'] = chumma
    if number == '1':
        data = db.session.query(RegisterMnmg).filter(RegisterMnmg.username == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for('deletetablerow', number = '1'))
    elif number == '2':
        data = db.session.query(CustomerDet).filter(CustomerDet.username == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for('deletetablerow', number = '2'))
    elif number == '3':
        data = db.session.query(Orders).filter(Orders.number == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for('deletetablerow', number = '3'))
    elif number == '4':
        data = db.session.query(PastOrders).filter(PastOrders.number == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for('deletetablerow', number = '4'))
    elif number == '5':
        data = db.session.query(StaffDet).filter(StaffDet.docid == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for('deletetablerow', number = '5'))
    elif number == '6':
        data = db.session.query(Appointments).filter(Appointments.id == chumma).first()
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for('deletetablerow', number = '6'))
    else:
        flash("No such table exists", "danger")
        return redirect(url_for('admindash'))
    return render_template("deletetablerow.html")

@app.route("/admin/table/row/add/<number>", methods = ['GET', 'POST'])
@is_admin
def addtablerow(number):
    session['number'] = number
    if number == '1':
        num = db.session.query(RegisterMnmg).count() + 1
        if request.method == 'POST':
            name = request.form['namehptl']
            user = request.form['username']
            password = sa.hash(request.form['password'])
            pin = request.form['pincode']
            address = request.form['address']
            data = RegisterMnmg(name, user, password, pin, address)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('admindash'))
        return render_template('addtablerow.html',a = '', num = num)
    elif number == '2':
        num = db.session.query(CustomerDet).count() + 1
        if request.method == 'POST':
            namecust = request.form['namecust']
            username = request.form['username']
            password = sa.hash(request.form['password'])
            pincode = request.form['pincode']
            address = request.form['address']
            gmail_id = request.form['gmail_id']
            aadhar = request.form['aadhar']
            age = request.form['age']
            gender = request.form['gender']
            prevmedrcrds = request.form['prevmedrcrds']
            data = CustomerDet(namecust, username, password, pincode, address, gmail_id, aadhar, age, gender, prevmedrcrds)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('admindash'))
        return render_template('addtablerow.html',b = '', num = num)
    elif number == '3':
        num = db.session.query(Orders).count() + 1
        if request.method == 'POST':
            usernamecust = request.form['username_cust']
            hptlusername = request.form['hptlusername']
            type = request.form['type']
            customer = db.session.query(CustomerDet).filter(CustomerDet.username == usernamecust).first()
            pincodecust = customer.pincode
            if hptlusername != "":
                address = customer.address
                namecust = customer.namecust
                aadhar = customer.aadhar
                age = customer.age
                gender = customer.gender
                prevmedrcrds = customer.prevmedrcrds
                data = Orders(hptlusername, usernamecust, type, address, namecust, aadhar, age, gender, prevmedrcrds)
                db.session.add(data)
                db.session.commit()
                return redirect(url_for('admindash'))
            return render_template('addtablerow.html',c = '', num = num, pat = usernamecust, patients = db.session.query(CustomerDet).all(), hospitals = db.session.query(RegisterMnmg).filter(RegisterMnmg.pincode == pincodecust).all())
        return render_template('addtablerow.html',c = '', num = num, pat = '', patients = db.session.query(CustomerDet).all(), hospitals = [])
    elif number == '4':
        num = db.session.query(PastOrders).count() + 1
        if request.method == 'POST':
            hptl = request.form['hptl']
            username = request.form['username_cust']
            type = request.form['type']
            customer = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
            patuser = customer.namecust
            pincodecust = customer.pincode
            if hptl != "":
                address = customer.address
                namecust = customer.namecust
                aadhar = customer.aadhar
                age = customer.age
                gender = customer.gender
                prevmedrcrds = customer.prevmedrcrds
                data = PastOrders(hptl, username, type, address, namecust, aadhar, age, gender, prevmedrcrds)
                db.session.add(data)
                db.session.commit()
                return redirect(url_for('admindash'))
            return render_template('addtablerow.html',d = '', num = num, pat = username, patients = db.session.query(CustomerDet).all(), hospitals = db.session.query(RegisterMnmg).filter(RegisterMnmg.pincode == pincodecust).all())
        return render_template('addtablerow.html',d = '', num = num, pat = '', patients = db.session.query(CustomerDet).all(), hospitals = [])
    elif number == '5':
        num = db.session.query(StaffDet).count() + 1
        if request.method == 'POST':
            name = request.form['name']
            age = request.form['age']
            gender = request.form['gender']
            salary = request.form['salary']
            spec = request.form['spec']
            hospitalid = request.form['hospitalid']
            data = StaffDet(name, age, gender, salary, spec, hospitalid)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('admindash'))
        return render_template('addtablerow.html',e = '', num = num, hospitals = db.session.query(RegisterMnmg).all())
    elif number == '6':
        num = db.session.query(Appointments).count() + 1
        if request.method == 'POST':
            patusername = request.form['patusername']
            hospuser = request.form['hospname']
            docname = request.form['docname']
            problem = request.form['problem']
            status = request.form['status']
            datetime = request.form['datetime']
            if docname != '':
                patient = db.session.query(CustomerDet).filter(CustomerDet.username == patusername).first()
                patname = patient.namecust
                staffdet = db.session.query(StaffDet).filter(StaffDet.hospitalid == hospuser, StaffDet.name == docname).first()
                specs = staffdet.spec
                n = datetime.find("T")
                date = datetime[:n:]
                time = datetime[n + 1::]
                data = Appointments(patname, patusername, problem, specs, docname, hospuser, date, time, status)
                db.session.add(data)
                db.session.commit()
                return redirect(url_for('admindash'))
            return render_template('addtablerow.html', f = '', num = num, patients = db.session.query(CustomerDet).all(), pat = patusername, hospitals = db.session.query(RegisterMnmg).all(), hosp = hospuser, doctors = db.session.query(StaffDet).filter(StaffDet.hospitalid == hospuser).all())
        return render_template('addtablerow.html',f = '', num = num, patients = db.session.query(CustomerDet).all(), hospitals = db.session.query(RegisterMnmg).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for('admindash'))
    return render_template('addtablerow.html')

@app.route("/admin/table/row/show/<number>", methods = ['GET', 'POST'])
@is_admin
def edittablerow(number):
    session['number'] = number
    if number == '1':
        return render_template('displaytables.html', a = '', registermnmg = db.session.query(RegisterMnmg).order_by(RegisterMnmg.username.asc()).all())
    elif number == '2':
        return render_template('displaytables.html', b = '', customerdet = db.session.query(CustomerDet).order_by(CustomerDet.custid.asc()).all())
    elif number == '3':
        return render_template('displaytables.html', c = '', orders = db.session.query(Orders).order_by(Orders.number.asc()).all())
    elif number == '4':
        return render_template('displaytables.html', d = '', pastorders = db.session.query(PastOrders).order_by(PastOrders.number.asc()).all())
    elif number == '5':
        return render_template('displaytables.html', e = '', staffdet = db.session.query(StaffDet).order_by(StaffDet.docid.asc()).all())
    elif number == '6':
        return render_template('displaytables.html', f = '', appoints = db.session.query(Appointments).order_by(Appointments.id.asc()).all())
    else:
        flash("No such table exists", "danger")
        return redirect(url_for('admindash'))
    return render_template('edittablerow.html')

@app.route("/admin/table/row/edit/<chumma>", methods = ['GET', 'POST'])
@is_admin
def editrow(chumma):
    number = session['number']
    if number == '1':
        user = db.session.query(RegisterMnmg).filter(RegisterMnmg.username == chumma).first()
        if request.method == 'POST':
            name = request.form['namehptl']
            username = request.form['username']
            password = sa.hash(request.form['password'])
            pincode = request.form['pincode']
            address = request.form['address']
            if name != '':
                user.namehptl = name
            if username != '':
                user.username = username
            if password != '':
                user.password = password
            if pincode != '':
                user.pincode = pincode
            if address != '':
                user.address = address
            db.session.commit()
            return redirect(url_for('edittablerow', number = '1'))
        return render_template('edittablerow.html', a = '', hospitals = db.session.query(RegisterMnmg).filter(RegisterMnmg.username == chumma).first())
    elif number == '2':
        user = db.session.query(CustomerDet).filter(CustomerDet.username == chumma).first()
        if request.method == 'POST':
            custid = request.form['custid']
            namecust = request.form['namecust']
            username = request.form['username']
            pincode = request.form['pincode']
            address = request.form['address']
            gmail_id = request.form['gmail_id']
            aadhar = request.form['aadhar']
            age = request.form['age']
            gender = request.form['gender']
            prevmedrcrds = request.form['prevmedrcrds']
            if custid != '':
                user.custid = custid
            if namecust != '':
                user.namecust = namecust
            if username != '':
                user.username = username
            if pincode != '':
                user.pincode = pincode
            if address != '':
                user.address = address
            if gmail_id != '':
                user.gmail_id = gmail_id
            if aadhar != '':
                user.aadhar = aadhar
            if age != '':
                user.age = age
            if gender != '':
                user.gender = gender
            if prevmedrcrds != '':
                user.prevmedrcrds = prevmedrcrds
            db.session.commit()
            return redirect(url_for('edittablerow', number = '2'))
        return render_template('edittablerow.html', b = '', customers = db.session.query(CustomerDet).filter(CustomerDet.username == chumma).first())
    elif number == '3':
        user = db.session.query(Orders).filter(Orders.number == chumma).first()
        if request.method == 'POST':
            number = request.form['number']
            hptl = request.form['hptl_username_in_vicinity']
            username_cust = request.form['username_cust']
            type = request.form['type']
            if number != '':
                user.number = number
            if hptl != '':
                user.hptl_username_in_vicinity = hptl
            if username_cust != '':
                user.username = username_cust
                customer = db.session.query(CustomerDet).filter(CustomerDet.username == username_cust).first()
                user.address = customer.address
                user.namecust = customer.namecust
                user.aadhar = customer.aadhar
                user.age = customer.age
                user.gender = customer.gender
                user.prevmedrcrds = customer.prevmedrcrds
            if type != '':
                user.type = type
            db.session.commit()
            return redirect(url_for('edittablerow', number = '3'))
        return render_template('edittablerow.html', c = '', orders = db.session.query(Orders).filter(Orders.number == chumma).first(), hosps = db.session.query(RegisterMnmg).all(), pats = db.session.query(CustomerDet).all())
    elif number == '4':
        user = db.session.query(PastOrders).filter(PastOrders.number == chumma).first()
        if request.method == 'POST':
            number = request.form['number']
            hptl = request.form['hptl']
            username_cust = request.form['username_cust']
            type = request.form['type']
            if number != '':
                user.number = number
            if hptl != '':
                user.hptl = hptl
            if username_cust != '':
                user.username_cust = username_cust
                customer = db.session.query(CustomerDet).filter(CustomerDet.username == username_cust).first()
                user.address = customer.address
                user.namecust = customer.namecust
                user.aadhar = customer.aadhar
                user.age = customer.age
                user.gender = customer.gender
                user.prevmedrcrds = customer.prevmedrcrds
            if type != '':
                user.type = type
            return redirect(url_for('edittablerow', number = '4'))
        return render_template('edittablerow.html', d = '', pastorders = db.session.query(PastOrders).filter(PastOrders.number == chumma).first(), hosps = db.session.query(RegisterMnmg).all(), pats = db.session.query(CustomerDet).all())
    elif number == '5':
        user = db.session.query(StaffDet).filter(StaffDet.docid == chumma).first()
        if request.method == 'POST':
            name = request.form['name']
            age = request.form['age']
            gender = request.form['gender']
            salary = request.form['salary']
            docid = request.form['docid']
            spec = request.form['spec']
            hospitalid = request.form['hospitalid']
            if name != '':
                user.name = name
            if age != '':
                user.age = age
            if gender != '':
                user.gender = gender
            if salary != '':
                user.salary = salary
            if docid != '':
                user.docid = docid
            if spec != '':
                user.spec = spec
            if hospitalid != '':
                user.hospitalid = hospitalid
            db.session.commit()
            return redirect(url_for('edittablerow', number = '5'))
        return render_template('edittablerow.html', e = '', staffdet = db.session.query(StaffDet).filter(StaffDet.docid == chumma).first())
    elif number == '6':
        c = 0
        user = db.session.query(Appointments).filter(Appointments.id == chumma).first()
        hospitall = user.HospName
        origstat = user.status
        if request.method == 'POST':
            num = request.form['id']
            patusername = request.form['patusername']
            hospname = request.form['hospname']
            docname = request.form['docname']
            problem = request.form['problem']
            specialisation = request.form['specs']
            status = request.form['status']
            datetime = request.form['datetime']
            if num != '':
                user.id = num
            if patusername != '':
                cust = db.session.query(CustomerDet).filter(CustomerDet.username == patusername).first()
                user.PatName = cust.namecust
                user.PatUsername = patusername
            if hospname != '':
                if docname != '':
                    user.HospName = hospname
                    docspec = db.session.query(StaffDet).filter(StaffDet.name == docname, StaffDet.hospitalid == hospname).first()
                    user.DocName = docname
                    user.Specialisation = docspec.spec
                    user.status = "Accepted"
                    c = 1
                else:
                    return render_template('edittablerow.html', f = '', appoints = db.session.query(Appointments).filter(Appointments.id == chumma).first(), hosp = hospname, hosps = db.session.query(RegisterMnmg).all(), pats = db.session.query(CustomerDet).all(), doc = docname, doctors = db.session.query(StaffDet).filter(StaffDet.hospitalid == hospname).all(), pat = patusername)
            if docname != '' and c == 0:
                user.DocName = docname
                docspec = db.session.query(StaffDet).filter(StaffDet.name == docname, StaffDet.hospitalid == hospitall).first()
                user.Specialisation = docspec.spec
            if problem != '':
                user.Problem = problem
            if specialisation != '':
                user.Specialisation = specialisation
            if status != '':
                if status == "None":
                    user.status = ""
                    user.DocName = ""
                    user.Specialisation = ""
                if status == "Accepted":
                    if docname != '' and c == 0:
                        user.status = status
                        user.DocName = docname
                        docspec = db.session.query(StaffDet).filter(StaffDet.name == docname, StaffDet.hospitalid == hospitall).first()
                        user.Specialisation = docspec.spec
                    else:
                        return render_template('edittablerow.html', f = '', appoints = db.session.query(Appointments).filter(Appointments.id == chumma).first(), doc = docname, doctors = db.session.query(StaffDet).filter(StaffDet.hospitalid == hospitall).all(), pat = patusername, stat = status)
                if status == "Declined":
                    user.status = status
                    user.DocName = ""
                    user.Specialisation = ""
            if datetime != '':
                user.datetime = datetime
            db.session.commit()
            return redirect(url_for('edittablerow', number = '6'))
        return render_template('edittablerow.html', f = '', appoints = db.session.query(Appointments).filter(Appointments.id == chumma).first(), hosps = db.session.query(RegisterMnmg).all(), pats = db.session.query(CustomerDet).all(), specs = db.session.query(StaffDet).distinct(StaffDet.spec).all(), doctors = db.session.query(StaffDet).filter(StaffDet.hospitalid == hospitall).all(), origstat = origstat)
    else:
        flash("No such table exists", "danger")
        return redirect(url_for('admindash'))
    return render_template('edittablerow.html')

@app.route("/admin/logout")
@is_admin
def logoutadmin():
    session.clear()
    return redirect(url_for('index'))
