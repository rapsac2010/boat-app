import os
from datetime import datetime, timedelta
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, jsonify
)
from werkzeug.exceptions import abort
from boatapp.auth import login_required
from boatapp.db import get_db, close_db
from boatapp.utils import voltage_to_percent, minutes_since_last_transmission


bp = Blueprint('dashboard', __name__)
print(__name__)

@bp.route('/')
def index():
    db = get_db()
    if g.user is not None:

        # Check if user has reservation today
        today = datetime.now().strftime('%Y-%m-%d')
        reservation = db.execute(
            """
            SELECT * FROM reservations WHERE renter_id = ? AND date(start_time) = ?
            """,
            (g.user['id'], today)
        ).fetchone()

        # print reservation for debug
        reservation_bool = False
        if reservation is not None:
            reservation_bool = True
            
            # In that case also get control status of boat controls
            boat_id = 1
            boat_control = db.execute(
                """
                SELECT * FROM boat_control WHERE id = ?
                """,
                (boat_id,)
            ).fetchone()
            boat_control_json = {col: boat_control[col] for col in boat_control.keys()}
            print(boat_control_json) # {'id': 1, 'boat_id': 1, 'last_updated': datetime.datetime(2023, 10, 10, 12, 47, 43), 'boat_on_lk': 0, 'boat_on_desired': 0, 'motor_lk': 0, 'motor_desired': 0, 'inverter_lk': 0, 'inverter_desired': 0, 'horn_lk': 
                                     # 0, 'horn_desired': 0, 'lights_fun_lk': 0, 'lights_fun_desired': 0, 'light_nav_lk': 0, 'light_nav_desired': 0}
        return render_template('dashboard/index.html', reservation=reservation_bool, boat_control=boat_control_json)
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/calendar')
@login_required
def calendar():
    return render_template('dashboard/calendar.html')

@bp.route('/get_update_data')
@login_required
def get_update_data():
    db = get_db()
    latest_row = db.execute(
        """
        SELECT * FROM boat_transmissions ORDER BY id DESC LIMIT 1
        """
    ).fetchone()

    if latest_row is not None:
        data = {col: latest_row[col] for col in latest_row.keys()}
        data['batteryPercentage'] = voltage_to_percent(data['voltage'])
        data['lastTransmission'] = minutes_since_last_transmission(data['time'])
        return jsonify(data), 200
    else:
        return jsonify({"error": "No data found"}), 404
