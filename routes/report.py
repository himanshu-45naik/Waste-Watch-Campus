import os
from flask import current_app
from routes import report_bp
from storage import db
from models import Building, Room, WasteReport
from forms import LoginForm, RegistrationForm, ReportForm
from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from utils import generate_image_filename
from services.llm_service import analyze_waste_image
import json
import logging

logger = logging.getLogger(__name__)

@report_bp.route('/report/<int:room_id>', methods=['GET', 'POST'])
@login_required
def report(room_id):
    room = Room.query.get_or_404(room_id)
    form = ReportForm()
    
    logger.debug(f"Processing report form for room {room_id}, is_submitted: {form.is_submitted()}")
    
    if form.validate_on_submit():
        try:
            logger.debug("Form validated successfully")
            # Create the report (without images initially)
            report = WasteReport(
                title=form.title.data,
                description=form.description.data,
                severity=form.severity.data,
                room_id=room.id,
                user_id=current_user.id,
                waste_type='Unknown',
                status='Pending'
            )
            logger.debug(f"Created report object with room_id: {report.room_id}")
            db.session.add(report)
            db.session.flush()  # Get the ID *after* adding to the session
            report_id = report.id

            uploaded_images = []
            # Process images (using the now-assigned report_id)
            for i in range(1, 6):
                image_field = getattr(form, f'image{i}')
                if image_field.data:
                    filename = secure_filename(generate_image_filename(report_id, i))
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    try:
                        image_field.data.save(filepath)
                        uploaded_images.append(filename)
                        # Gemini analysis (only for the first image)
                        if i == 1:
                            try:
                                with open(filepath, "rb") as img_file:
                                    image_bytes = img_file.read()
                                    waste_type, severity = analyze_waste_image(image_bytes)
                                    report.waste_type = waste_type
                                    if form.severity.data == "Unknown":
                                        report.severity = severity
                            except Exception as gemini_e:
                                logger.error(f"Gemini API error: {gemini_e}")
                                flash(f"Gemini analysis failed: {gemini_e}", 'warning') #Inform user about failure
                    except Exception as image_e:
                        logger.error(f"Image save error: {image_e}")
                        flash(f"Error saving image {i}: {image_e}", 'danger')
                        db.session.rollback() # Rollback changes if image saving fails
                        return redirect(url_for('report.report', room_id=room_id)) # Redirect back to the form

            report.images = json.dumps(uploaded_images)
            db.session.commit()
            logger.debug(f"Report committed to DB with ID: {report.id}")
            flash('Waste report submitted successfully!', 'success')
            return redirect(url_for('main.room', room_id=room_id))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            logger.exception(f"Error submitting report: {e}")
            return redirect(url_for('report.report', room_id=room_id))
    else:
        if form.is_submitted():
            logger.debug(f"Form validation failed: {form.errors}")

    return render_template('report.html', form=form, room=room)

@report_bp.route('/update_status/<int:report_id>', methods=['POST'])
@login_required
def update_status(report_id):
    if current_user.user_type != 'cleaning_staff':
        return jsonify({'success': False, 'message': 'Unauthorized'})

    try:
        report = WasteReport.query.get(report_id) # Corrected line
        if report is None:
            return jsonify({'success': False, 'message': 'Report not found'})
        if report.status == 'pending':
            report.status = 'completed'
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Report already updated'})
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error updating report status: {e}") # Use logger.exception for better debugging info
        return jsonify({'success': False, 'message': 'An unexpected error occurred'})


@report_bp.route('/debug_reports')
@login_required
def debug_reports():
    all_reports = WasteReport.query.all()
    logger.debug(f"Found {len(all_reports)} total reports in database")
    
    result = []
    for report in all_reports:
        result.append({
            'id': report.id,
            'title': report.title,
            'room_id': report.room_id,
            'user_id': report.user_id,
            'created_at': str(report.created_at),
            'waste_type': report.waste_type,
            'severity': report.severity,
            'status': report.status
        })
    
    return jsonify(result)