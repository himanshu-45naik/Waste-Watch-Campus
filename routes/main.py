from routes import main_bp
from storage import db
from models import Building, Room, WasteReport, Floor
from flask import render_template
from utils import get_severity_badge_class, get_waste_type_icon, get_status_badge_class
import logging

logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    buildings = Building.query.all()
    return render_template('index.html', buildings=buildings, Floor=Floor, Room=Room)

@main_bp.route('/building/<int:building_id>')
def building(building_id):
    building = Building.query.get_or_404(building_id)
    floors = Floor.query.filter_by(building_id=building_id).order_by(Floor.level).all()
    return render_template('building.html', building=building, floors=floors)

@main_bp.route('/room/<int:room_id>')
def room(room_id):
    room = Room.query.get_or_404(room_id)
    logger.debug(f"Fetching reports for room {room_id}")
    reports = WasteReport.query.filter_by(room_id=room_id).order_by(WasteReport.created_at.desc()).all()
    logger.debug(f"Found {len(reports)} reports for room {room_id}")
    
    # Log each report for debugging
    for report in reports:
        logger.debug(f"Report ID: {report.id}, Title: {report.title}, Room ID: {report.room_id}")
    
    return render_template('room.html', room=room, reports=reports,
                          get_severity_badge_class=get_severity_badge_class,
                          get_waste_type_icon=get_waste_type_icon,
                          get_status_badge_class=get_status_badge_class)