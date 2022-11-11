from datetime import datetime
from flask_login import UserMixin
# import sqlalchemy as db
from . import db
from .enums import Roles, ScanTypes
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    
    __tablename__ = 'users'
    id = db.Column(
        db.Integer,
        nullable = False,
        primary_key = True
    )
    
    medical_id = db.Column(
        db.Integer,
        nullable = False,
        unique = True
    )
    
    first_name = db.Column(
        db.String(100),
        nullable = False,
        unique = False
    )
    
    last_name = db.Column(
        db.String(100),
        nullable = False,
        unique = False
    )
    
    phone_no = db.Column(
        db.String(14),
        unique = True,
        nullable = True
    )
    
    email = db.Column(
        db.String(40),
        unique = True,
        nullable = False
    )
    
    role = db.Column(
        db.Enum(Roles),
        nullable = True
    )
    
    password = db.Column(
        db.String(200),
        unique = True,
        nullable = False
    )
    
    scans = db.relationship("Scan", backref='users', lazy = True)
    
    created_on = db.Column(
        db.DateTime,
        index = False,
        unique = False,
        nullable = True
    )
    
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self) -> str:
        return '<User {}>'.format(self.first_name + self.last_name)


class Scan(db.Model):
    
    __tablename__ = 'scans'
    
    id = db.Column(
        db.Integer,
        nullable = False,
        primary_key = True
    )
    
    scan_file = db.Column(
        db.String(100),
        nullable = False,
        unique = False
    )
    
    scan_type = db.Column(
        db.Enum(ScanTypes),
        nullable = False
    )
    
    created_on = db.Column(
        db.DateTime,
        index = False,
        unique = False,
        default = datetime.now()
    )
    
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'))    