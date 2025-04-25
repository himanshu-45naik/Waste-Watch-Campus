from storage import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # student, teacher, cleaning_staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reports = db.relationship('WasteReport', backref='reporter', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    rooms = db.relationship('Room', backref='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    floors = db.relationship('Floor', backref='building', lazy='dynamic')
    
    def __repr__(self):
        return f'<Building {self.name}>'

class Floor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 0 for ground floor, 1 for first floor, etc.
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    
    # Relationships
    rooms = db.relationship('Room', backref='floor', lazy='dynamic')
    
    def __repr__(self):
        return f'<Floor {self.name} in {self.building.name}>'

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(20), nullable=False)  # classroom, lab
    floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    
    # Relationships
    reports = db.relationship('WasteReport', backref='room', lazy='dynamic')
    
    def __repr__(self):
        return f'<Room {self.room_number} - {self.name}>'

class WasteReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    images = db.Column(db.Text, nullable=True)  # JSON string of image filenames
    waste_type = db.Column(db.String(50), nullable=False)  # paper, plastic, e-waste, etc.
    severity = db.Column(db.String(20), nullable=False)  # critical, high, medium, low
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, in_progress, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def get_images(self):
        if not self.images:
            return []
        return json.loads(self.images)
    
    def __repr__(self):
        return f'<WasteReport {self.id} - {self.title}>'
