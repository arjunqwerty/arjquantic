from zorgapp import db

class RegisterMnmg(db.Model):
    __tablename__ = 'hospdetails'
    namehptl = db.Column(db.String(200))
    username = db.Column(db.String(200), primary_key = True)
    password = db.Column(db.String(300))
    pincode = db.Column(db.String(10))
    address = db.Column(db.Text())

    def __init__(self, namehptl, username, password, pincode, address):
        self.namehptl = namehptl
        self.username = username
        self.password = password
        self.pincode = pincode
        self.address = address

class CustomerDet(db.Model):
    __tablename__ = 'custdetails'
    custid = db.Column(db.Integer, primary_key = True)
    namecust = db.Column(db.String(200))
    username = db.Column(db.String(200))
    password = db.Column(db.String(300))
    pincode = db.Column(db.String(10))
    address = db.Column(db.Text())
    gmail_id = db.Column(db.String(200))
    aadhar = db.Column(db.String(20))
    age = db.Column(db.String(5))
    gender = db.Column(db.String(1))
    prevmedrcrds = db.Column(db.Text())

    def __init__(self, namecust, username, password, pincode, address, gmail_id, aadhar, age, gender, prevmedrcrds):
        self.namecust = namecust
        self.username = username
        self.password = password
        self.pincode = pincode
        self.address = address
        self.gmail_id = gmail_id
        self.aadhar = aadhar
        self.age = age
        self.gender = gender
        self.prevmedrcrds = prevmedrcrds

class Appointments(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key = True)
    PatName = db.Column(db.String(50))
    PatUsername = db.Column(db.String(50))
    Problem = db.Column(db.Text())
    Specialisation = db.Column(db.String(50))
    DocName = db.Column(db.String(50))
    HospName = db.Column(db.String(50))
    date = db.Column(db.String(10))
    time = db.Column(db.String(5))
    status = db.Column(db.String(20))

    def __init__(self, PatName, PatUsername, Problem, Specialisation, DocName, HospName, date, time, status):
        self.PatName = PatName
        self.PatUsername = PatUsername
        self.Problem = Problem
        self.Specialisation = Specialisation
        self.DocName = DocName
        self.HospName = HospName
        self.date = date
        self.time = time
        self.status = status

class Orders(db.Model):
    __tablename__ = 'orders'
    number = db.Column(db.Integer, primary_key = True)
    hptl_username_in_vicinity = db.Column(db.String(200))
    username_cust = db.Column(db.String(200))
    type = db.Column(db.String(50))
    address = db.Column(db.Text())
    namecust = db.Column(db.String(200))
    aadhar = db.Column((db.String(20)))
    age = db.Column(db.String(5))
    gender = db.Column(db.String(1))
    prevmedrcrds = db.Column(db.Text())

    def __init__(self, hptl_username_in_vicinity, username_cust, type, address, namecust, aadhar, age, gender, prevmedrcrds):
        self.hptl_username_in_vicinity = hptl_username_in_vicinity
        self.username_cust = username_cust
        self.type = type
        self.address = address
        self.namecust = namecust
        self.aadhar = aadhar
        self.age = age
        self.gender = gender
        self.prevmedrcrds = prevmedrcrds

class PastOrders(db.Model):
    __tablename__ = 'pastorders'
    number = db.Column(db.Integer, primary_key = True)
    name_of_hptl_accepting_responsibilty = db.Column(db.String(200))
    username_cust = db.Column(db.String(200))
    type = db.Column(db.String(50))
    address = db.Column(db.Text())
    namecust = db.Column(db.String(200))
    aadhar = db.Column(db.String(20))
    age = db.Column(db.String(5))
    gender = db.Column(db.String(1))
    prevmedrcrds = db.Column(db.Text())

    def __init__(self, name_of_hptl_accepting_responsibilty, username_cust, type, address, namecust, aadhar, age, gender, prevmedrcrds):
        self.name_of_hptl_accepting_responsibilty = name_of_hptl_accepting_responsibilty
        self.username_cust = username_cust
        self.type = type
        self.address = address
        self.namecust = namecust
        self.aadhar = aadhar
        self.age = age
        self.gender = gender
        self.prevmedrcrds = prevmedrcrds

class StaffDet(db.Model):
    __tablename__ = 'staffdetails'
    name = db.Column(db.String(200))
    age = db.Column(db.String(20))
    gender = db.Column(db.String(4))
    salary = db.Column(db.String(10))
    docid = db.Column(db.Integer, primary_key = True)
    spec = db.Column(db.String(200))
    hospitalid = db.Column(db.String(200))

    def __init__(self, name, age, gender, salary, spec, hospitalid):
        self.name = name
        self.age = age
        self.gender = gender
        self.salary = salary
        self.spec = spec
        self.hospitalid = hospitalid
