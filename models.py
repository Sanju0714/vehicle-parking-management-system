from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(10))
    phone = db.Column(db.String(15))
    role = db.Column(db.String(10))  # 'admin' or 'user'

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(6))
    price_per_hour = db.Column(db.Float)
    max_spots = db.Column(db.Integer)
    
    spots = db.relationship('Spot', back_populates='lot', cascade='all, delete-orphan')  # <-- FIXED


class Spot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    lot = db.relationship('ParkingLot', back_populates='spots')  # <-- FIXED

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('spot.id'), nullable=True)
    vehicle_number = db.Column(db.String(20)) 
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    cost = db.Column(db.Float) 

    user = db.relationship('User', backref='reservations')
    lot = db.relationship('ParkingLot', backref='reservations')
    spot = db.relationship('Spot', backref='reservations')

