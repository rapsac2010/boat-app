from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, jsonify
)
from boatapp.auth import login_required
from boatapp.db import get_db, close_db


bp = Blueprint('control', __name__, url_prefix = '/control')

@bp.route('/control-boat', methods=('POST',))
def control_boat():
    db = get_db()
    
    # Get status of boat
    boat_id = 1 # Only one boat at the moment, so hardcoded boat id
    boat_control_row = db.execute(
        """
        SELECT * FROM boat_control WHERE id = ?
        """,
        (boat_id,)
    ).fetchone()
    # to json
    boat_control = {col: boat_control_row[col] for col in boat_control_row.keys()}

    content = request.get_json()

    # return boat control
    return jsonify(boat_control), 200
