from routes import leaderboard_bp
from flask import render_template
from storage import db
from models import Department, Room, Building, Floor, WasteReport

@leaderboard_bp.route('/leaderboard')
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
    
    # Group buildings by college type
    college_groups = {
        "D.Y. Patil College of Engineering": [],
        "D.Y. Patil Junior College": [],
        "D.Y. Patil International University": [],
        "D.Y. Patil College of Architecture": [],
    }
    
    # Assign buildings to their college group
    all_buildings = Building.query.all()
    for building in all_buildings:
        if "Engineering" in building.name:
            college_groups["D.Y. Patil College of Engineering"].append(building)
        elif "Junior College" in building.name:
            college_groups["D.Y. Patil Junior College"].append(building)
        elif "International" in building.name:
            college_groups["D.Y. Patil International University"].append(building)
        elif "Architecture" in building.name:
            college_groups["D.Y. Patil College of Architecture"].append(building)
        
    
    
    college_data = {}
    
    for college_name, buildings in college_groups.items():
        # Skip empty college groups
        if not buildings:
            continue
            
        # Get all floors in these buildings
        building_ids = [building.id for building in buildings]
        floors = Floor.query.filter(Floor.building_id.in_(building_ids)).all()
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
        
        # Only add this college if it has at least one department with data
        if college_departments:
            college_data[college_name] = college_departments
    
    return render_template('leaderboard.html', 
                          overall_scores=department_scores, 
                          college_data=college_data)
