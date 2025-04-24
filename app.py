import os
import logging
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import json
import google.generativeai as genai
from datetime import datetime
import base64

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Setup the database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///waste_management.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB limit for uploads

# Configure API key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your-gemini-api-key")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the database
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Create upload folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Import models after db initialization
with app.app_context():
    from models import User, Building, Floor, Room, WasteReport, Department
    import models  # noqa: F401
    from utils import get_severity_badge_class, get_waste_type_icon, get_status_badge_class
    db.create_all()
    
    # Initialize campus data if not exists
    if Building.query.count() == 0:
        # Initialize campus data
        try:
            # Define the colleges and their departments
            colleges = {
                "D.Y. Patil Engineering A Wing": {
                    "floors": 3,  # Ground + 2 floors
                    "classrooms": 15,
                    "labs": 10,
                    "departments": ["Computer Science", "Artificial Intelligence"]
                },
                "D.Y. Patil Engineering B Wing": {
                    "floors": 3,  # Ground + 2 floors
                    "classrooms": 12,
                    "labs": 8,
                    "departments": ["Information Technology"]
                },
                "D.Y. Patil Engineering C Wing": {
                    "floors": 3,  # Ground + 2 floors
                    "classrooms": 15,
                    "labs": 9,
                    "departments": ["Mechanical"]
                },
                "D.Y. Patil Engineering D Wing": {
                    "floors": 3,  # Ground + 2 floors
                    "classrooms": 12,
                    "labs": 8,
                    "departments": ["Instrumentation"]
                },
                "D.Y. Patil Engineering E Wing": {
                    "floors": 3,  # Ground + 2 floors
                    "classrooms": 10,
                    "labs": 7,
                    "departments": ["Civil"]
                },
                "D.Y. Patil Junior College": {
                    "floors": 3,  # Ground + 2 floors
                    "classrooms": 20,
                    "labs": 7,
                    "departments": ["Science", "Commerce", "Arts"]
                },
                "D.Y. Patil International University": {
                    "floors": 6,  # Ground + 5 floors
                    "classrooms": 30,
                    "labs": 15,
                    "departments": ["Computer Science", "Artificial Intelligence"]
                },
                "D.Y. Patil College of Architecture": {
                    "floors": 3,  # Ground + 2 floors
                    "classrooms": 15,
                    "labs": 5,
                    "departments": ["Architecture"]
                },
                "D.Y. Patil Robotics & Automation Lab": {
                    "floors": 2,  # Ground + 1 floor
                    "classrooms": 5,
                    "labs": 10,
                    "departments": ["Robotics and Automation"]
                }
            }
            
            # Create departments
            all_departments = set()
            for college_data in colleges.values():
                for dept in college_data["departments"]:
                    all_departments.add(dept)
            
            for dept_name in all_departments:
                if not Department.query.filter_by(name=dept_name).first():
                    department = Department(name=dept_name)
                    db.session.add(department)
            
            db.session.commit()
            
            # Create buildings, floors, and rooms
            for college_name, college_data in colleges.items():
                # Create building
                building = Building(name=college_name)
                db.session.add(building)
                db.session.flush()  # Get the ID
                
                departments = [Department.query.filter_by(name=dept_name).first() 
                              for dept_name in college_data["departments"]]
                
                # Distribute classrooms and labs across floors and departments
                classrooms_per_floor = college_data["classrooms"] // college_data["floors"]
                labs_per_floor = college_data["labs"] // college_data["floors"]
                
                # Create floors
                for floor_num in range(college_data["floors"]):
                    floor_name = "Ground Floor" if floor_num == 0 else f"Floor {floor_num}"
                    floor = Floor(name=floor_name, building_id=building.id, level=floor_num)
                    db.session.add(floor)
                    db.session.flush()  # Get the ID
                    
                    # Create classrooms
                    for i in range(classrooms_per_floor):
                        room_number = f"{floor_num}{i+1:02d}"
                        dept = departments[i % len(departments)]
                        room = Room(
                            room_number=room_number,
                            name=f"Classroom {room_number}",
                            floor_id=floor.id,
                            department_id=dept.id,
                            room_type="classroom"
                        )
                        db.session.add(room)
                    
                    # Create labs
                    for i in range(labs_per_floor):
                        room_number = f"L{floor_num}{i+1:02d}"
                        dept = departments[i % len(departments)]
                        room = Room(
                            room_number=room_number,
                            name=f"Lab {room_number}",
                            floor_id=floor.id,
                            department_id=dept.id,
                            room_type="lab"
                        )
                        db.session.add(room)
            
            db.session.commit()
            
            # Create a test user
            if User.query.filter_by(username='testuser').first() is None:
                test_user = User(
                    username='testuser',
                    email='test@example.com',
                    user_type='student'
                )
                test_user.set_password('password123')
                db.session.add(test_user)
                db.session.commit()
                logger.info("Test user created successfully")
                
            # Create a test user for cleaning staff
            if User.query.filter_by(username='cleaning').first() is None:
                staff_user = User(
                    username='cleaning',
                    email='cleaning@example.com',
                    user_type='cleaning_staff'
                )
                staff_user.set_password('password123')
                db.session.add(staff_user)
                db.session.commit()
                logger.info("Cleaning staff user created successfully")
                
            logger.info("Campus data initialized successfully")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing campus data: {str(e)}")

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Import forms after importing models
from forms import LoginForm, RegistrationForm, ReportForm

# Routes
@app.route('/')
def index():
    buildings = Building.query.all()
    return render_template('index.html', buildings=buildings, Floor=Floor, Room=Room)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            user_type=form.user_type.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    user_reports = WasteReport.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', reports=user_reports,
                          get_severity_badge_class=get_severity_badge_class,
                          get_waste_type_icon=get_waste_type_icon,
                          get_status_badge_class=get_status_badge_class)

@app.route('/building/<int:building_id>')
def building(building_id):
    building = Building.query.get_or_404(building_id)
    floors = Floor.query.filter_by(building_id=building_id).order_by(Floor.level).all()
    return render_template('building.html', building=building, floors=floors)

@app.route('/room/<int:room_id>')
def room(room_id):
    room = Room.query.get_or_404(room_id)
    reports = WasteReport.query.filter_by(room_id=room_id).order_by(WasteReport.created_at.desc()).all()
    return render_template('room.html', room=room, reports=reports,
                          get_severity_badge_class=get_severity_badge_class,
                          get_waste_type_icon=get_waste_type_icon,
                          get_status_badge_class=get_status_badge_class)

@app.route('/report/<int:room_id>', methods=['GET', 'POST'])
@login_required
def report(room_id):
    room = Room.query.get_or_404(room_id)
    form = ReportForm()
    
    if form.validate_on_submit():
        try:
            report = WasteReport(
                title=form.title.data,
                description=form.description.data,
                severity=form.severity.data,
                room_id=room.id,
                user_id=current_user.id,
                waste_type='Unknown',  # Will be updated by Gemini
                status='Pending'
            )
            db.session.add(report)
            db.session.flush()  # Get the report ID
            
            # Process images
            uploaded_images = []
            for i in range(1, 6):  # Handle up to 5 images
                image_field = getattr(form, f'image{i}')
                if image_field.data:
                    filename = secure_filename(f"report_{report.id}_img{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image_field.data.save(filepath)
                    uploaded_images.append(filename)
                    
                    # For the first image, analyze with Gemini for waste classification
                    if i == 1:
                        try:
                            # Get the waste type prediction from Gemini
                            with open(filepath, "rb") as img_file:
                                image_bytes = img_file.read()
                                waste_type, severity = analyze_waste_image(image_bytes)
                                report.waste_type = waste_type
                                # Only override severity if user selected "Unknown"
                                if form.severity.data == "Unknown":
                                    report.severity = severity
                        except Exception as e:
                            logger.error(f"Error analyzing image with Gemini: {str(e)}")
            
            report.images = json.dumps(uploaded_images)
            db.session.commit()
            
            flash('Waste report submitted successfully!', 'success')
            return redirect(url_for('room', room_id=room.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting report: {str(e)}', 'danger')
    
    return render_template('report.html', form=form, room=room)

@app.route('/leaderboard')
def leaderboard():
    # Get all departments
    departments = Department.query.all()
    
    # Calculate department scores
    department_scores = []
    for dept in departments:
        # Count all reports submitted for rooms in this department
        rooms = Room.query.filter_by(department_id=dept.id).all()
        room_ids = [room.id for room in rooms]
        report_count = WasteReport.query.filter(WasteReport.room_id.in_(room_ids)).count()
        
        department_scores.append({
            'department': dept,
            'report_count': report_count
        })
    
    # Sort by report count (descending)
    department_scores.sort(key=lambda x: x['report_count'], reverse=True)
    
    # Group by college
    colleges = Building.query.all()
    college_data = {}
    
    for college in colleges:
        # Get all floors in this building
        floors = Floor.query.filter_by(building_id=college.id).all()
        floor_ids = [floor.id for floor in floors]
        
        # Get all rooms in these floors
        rooms = Room.query.filter(Room.floor_id.in_(floor_ids)).all()
        
        # Group rooms by department
        dept_data = {}
        for room in rooms:
            dept_id = room.department_id
            if dept_id not in dept_data:
                dept_data[dept_id] = {
                    'department': Department.query.get(dept_id),
                    'rooms': [],
                    'report_count': 0
                }
            dept_data[dept_id]['rooms'].append(room)
            
            # Count reports for this room
            report_count = WasteReport.query.filter_by(room_id=room.id).count()
            dept_data[dept_id]['report_count'] += report_count
        
        # Convert to list and sort by report count
        college_departments = list(dept_data.values())
        college_departments.sort(key=lambda x: x['report_count'], reverse=True)
        
        college_data[college.name] = college_departments
    
    return render_template('leaderboard.html', 
                          overall_scores=department_scores, 
                          college_data=college_data)

def analyze_waste_image(image_bytes):
    """
    Analyze an image using Google's Gemini API to classify waste type and severity
    """
    try:
        # Convert image to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Prepare the prompt
        prompt = """
        Analyze this image of waste in a classroom or lab setting. Please identify:
        1. What type of waste is visible (e.g., Paper, Plastic, E-waste, Food waste, Mixed waste, Hazardous)
        2. How severe is the waste situation (Critical, High, Medium, Low)
        
        Format your response as a JSON object with two fields: waste_type and severity.
        Example: {"waste_type": "Paper", "severity": "Medium"}
        """
        
        # Prepare the image for the model
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": image_b64
            }
        ]
        
        # Generate content
        response = model.generate_content([prompt, image_parts])
        
        # Extract the response
        response_text = response.text
        
        # Try to parse the JSON response
        try:
            # Find JSON content in the response (might be surrounded by backticks or other text)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                waste_type = result.get('waste_type', 'Unknown')
                severity = result.get('severity', 'Unknown')
                return waste_type, severity
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
        
        # Fallback: simple text parsing if JSON parsing fails
        if "paper" in response_text.lower():
            waste_type = "Paper"
        elif "plastic" in response_text.lower():
            waste_type = "Plastic"
        elif "e-waste" in response_text.lower() or "electronic" in response_text.lower():
            waste_type = "E-waste"
        elif "food" in response_text.lower():
            waste_type = "Food waste"
        elif "hazard" in response_text.lower():
            waste_type = "Hazardous"
        else:
            waste_type = "Mixed waste"
        
        if "critical" in response_text.lower():
            severity = "Critical"
        elif "high" in response_text.lower():
            severity = "High"
        elif "medium" in response_text.lower():
            severity = "Medium"
        elif "low" in response_text.lower():
            severity = "Low"
        else:
            severity = "Unknown"
        
        return waste_type, severity
    
    except Exception as e:
        logger.error(f"Error in Gemini analysis: {str(e)}")
        return "Unknown", "Unknown"

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
