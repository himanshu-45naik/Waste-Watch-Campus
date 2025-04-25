import os
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime
import io

      
def save_image(image_data, filename, upload_folder):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    try:
        image_data.save(filepath)
        return filepath
    except Exception as e:
        print("No image saved")
        return None  # Indicate failure

    
      
import random
import string

def generate_image_filename(report_id: int, image_number: int) -> str:
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"report_{report_id}_img{image_number}_{timestamp}_{random_part}.jpg"

    

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
