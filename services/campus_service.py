from storage import db
from models import User, Building, Floor, Room, Department
import logging

logger = logging.getLogger(__name__)


def initialize_campus_data():
    """Initialize campus buildings, departments, and test users."""
    if Building.query.count() > 0:
        logger.info("Campus data already exists, skipping initialization")
        return

    try:
        colleges = {
            "D.Y. Patil Engineering A Wing": {
                "floors": 3,
                "classrooms": 15,
                "labs": 10,
                "departments": ["Computer Science", "Artificial Intelligence"]
            },
            "D.Y. Patil Engineering B Wing": {
                "floors": 3,
                "classrooms": 12,
                "labs": 8,
                "departments": ["Information Technology"]
            },
            "D.Y. Patil Engineering C Wing": {
                "floors": 3,
                "classrooms": 15,
                "labs": 9,
                "departments": ["Mechanical"]
            },
            "D.Y. Patil Engineering D Wing": {
                "floors": 3,
                "classrooms": 12,
                "labs": 8,
                "departments": ["Instrumentation"]
            },
            "D.Y. Patil Engineering E Wing": {
                "floors": 3,
                "classrooms": 10,
                "labs": 7,
                "departments": ["Civil"]
            },
            "D.Y. Patil Junior College": {
                "floors": 3,
                "classrooms": 20,
                "labs": 7,
                "departments": ["Science", "Commerce", "Arts"]
            },
            "D.Y. Patil International University": {
                "floors": 6,
                "classrooms": 30,
                "labs": 15,
                "departments": ["Computer Science", "Artificial Intelligence"]
            },
            "D.Y. Patil College of Architecture": {
                "floors": 3,
                "classrooms": 15,
                "labs": 5,
                "departments": ["Architecture"]
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
            db.session.flush()

            departments = [
                Department.query.filter_by(name=dept_name).first()
                for dept_name in college_data["departments"]
            ]

            classrooms_per_floor = college_data["classrooms"] // college_data["floors"]
            labs_per_floor = college_data["labs"] // college_data["floors"]

            # Create floors
            for floor_num in range(college_data["floors"]):
                floor_name = "Ground Floor" if floor_num == 0 else f"Floor {floor_num}"
                floor = Floor(
                    name=floor_name,
                    building_id=building.id,
                    level=floor_num
                )
                db.session.add(floor)
                db.session.flush()

                # Create classrooms
                for i in range(classrooms_per_floor):
                    room_number = f"{floor_num}{i + 1:02d}"
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
                    room_number = f"L{floor_num}{i + 1:02d}"
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


        logger.info("Campus data initialized successfully")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error initializing campus data: {str(e)}")

def initialize_test_users():
    # Create a test user
        if User.query.filter_by(username="testuser").first() is None:
            test_user = User(
                username="testuser",
                email="test@example.com",
                user_type="student"
            )
            test_user.set_password("password123")
            db.session.add(test_user)
            db.session.commit()
            logger.info("Test user created successfully")

        # Create a test user for cleaning staff
        if User.query.filter_by(username="cleaning").first() is None:
            staff_user = User(
                username="cleaning",
                email="cleaning@example.com",
                user_type="cleaning_staff"
            )
            staff_user.set_password("password123")
            db.session.add(staff_user)
            db.session.commit()
            logger.info("Cleaning staff user created successfully")