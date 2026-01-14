from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
report_bp = Blueprint('report', __name__)
leaderboard_bp = Blueprint('leaderboard', __name__)

# Import routes to register them with blueprints
# This MUST come after blueprint creation to avoid circular imports
from routes import auth, main, report, leaderboard

# Export blueprints for easy importing
__all__ = ['auth_bp', 'main_bp', 'report_bp', 'leaderboard_bp']