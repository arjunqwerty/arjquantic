from zorgapp import db

class Camera(db.Model):
    __tablename__ = 'cameras'
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

