import os
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime

def save_image(image_data, filename, upload_folder):
    """
    Save an image to the specified upload folder
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    filepath = os.path.join(upload_folder, filename)
    image_data.save(filepath)
    return filepath

def generate_image_filename(report_id, image_number):
    """
    Generate a unique filename for an uploaded image
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"report_{report_id}_img{image_number}_{timestamp}.jpg"

def get_severity_badge_class(severity):
    """
    Return the appropriate Bootstrap badge class for a given severity level
    """
    severity_classes = {
        'Critical': 'bg-danger',
        'High': 'bg-warning',
        'Medium': 'bg-info',
        'Low': 'bg-success',
        'Unknown': 'bg-secondary'
    }
    return severity_classes.get(severity, 'bg-secondary')

def get_waste_type_icon(waste_type):
    """
    Return the appropriate icon class for a given waste type
    """
    waste_icons = {
        'Paper': 'fa-newspaper',
        'Plastic': 'fa-wine-bottle',
        'E-waste': 'fa-laptop',
        'Food waste': 'fa-apple-alt',
        'Hazardous': 'fa-skull-crossbones',
        'Mixed waste': 'fa-trash',
        'Unknown': 'fa-question'
    }
    return waste_icons.get(waste_type, 'fa-trash')

def get_status_badge_class(status):
    """
    Return the appropriate Bootstrap badge class for a given status
    """
    status_classes = {
        'Pending': 'bg-warning',
        'In Progress': 'bg-info',
        'Resolved': 'bg-success'
    }
    return status_classes.get(status, 'bg-secondary')
