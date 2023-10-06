import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, jsonify
)
from werkzeug.exceptions import abort
from boatapp.auth import login_required
from boatapp.db import get_db
from boatapp.utils import voltage_to_percent, minutes_since_last_transmission

bp = Blueprint('blog', __name__)
print(__name__)

@bp.route('/')
def index():
    db = get_db()
    if g.user is not None:
        pf_path = url_for('static', filename=f"uploads/images/{g.user['profile_fname']}")
        return render_template('dashboard/index.html', pf_path = pf_path)
    else:
        return redirect(url_for('auth.login'))
    


@bp.route('/get_update_data')
@login_required
def get_update_data():
    db = get_db()
    latest_row = db.execute(
        """
        SELECT * FROM boat ORDER BY id DESC LIMIT 1
        """
    ).fetchone()

    if latest_row is not None:
        data = {col: latest_row[col] for col in latest_row.keys()}
        data['batteryPercentage'] = voltage_to_percent(data['voltage'])
        data['lastTransmission'] = minutes_since_last_transmission(data['time'])
        return jsonify(data), 200
    else:
        return jsonify({"error": "No data found"}), 404

# @bp.route('/create', methods = ('GET', 'POST'))
# @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required'
        
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute("""
#                 INSERT INTO post (title, body, author_id)
#                  VALUES (?, ?, ?)
#             """, (title, body, g.user['id']))
#             db.commit()
#             return redirect(url_for('blog.index')) #what happens if index here
#     return render_template('blog/create.html')

# @bp.route('/<int:id>/update', methods = ('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)

#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required'
        
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE post SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))
        
#     return render_template('blog/update.html', post = post)

# @bp.route('/<int:id>/delete', methods = ('POST',))
# @login_required
# def delete(id):
#     post = get_post(id)
#     db = get_db()
#     db.execute(
#         'DELETE FROM post WHERE id = ?', (id,)
#     )
#     db.commit()
#     return redirect(url_for('blog.index'))