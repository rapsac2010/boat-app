import os
import locale
from datetime import datetime, timedelta
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, jsonify
)
from boatapp.auth import login_required
from boatapp.db import get_db, close_db
from boatapp.utils import get_public_url
from boatapp.payments import get_client
from mollie.api.client import Client
from mollie.api.error import Error

# TODO: user can edit price by editing the HTML, fix this by taking price from database
locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')

bp = Blueprint('reservations', __name__, url_prefix = '/reservations')

@bp.route('/my_bookings', methods=('GET',))
@login_required
def my_bookings():

    payment_status = request.args.get('payment_status')
    db = get_db()
    reservations = db.execute(
        """
        SELECT id, start_time, price, payment_status, mollie_payment_id FROM reservations
        WHERE renter_id = ?
        """,
        (g.user['id'],)
    ).fetchall()

    mollie_client = get_client()
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')

    # Convert events to a format suitable for FullCalendar
    reserve_list_user = [
        {
            'reserve_id': reservation[0],
            'date': reservation[1].strftime('%Y-%m-%d'),
            'date_title': reservation[1].strftime('%d %B %Y'),
            "payed": reservation[3],
            "price": reservation[2]
        }
        for reservation in reservations
    ]
    locale.setlocale(locale.LC_TIME, 'C')
    
    # sort reservations by date
    reserve_list_user.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

    close_db()

    return render_template(
        'dashboard/myBookings.html', 
        reservations=reserve_list_user, 
        now = datetime.now().strftime('%Y-%m-%d'), 
        payment_status = payment_status)


# TODO: check if there is a reservation for the given date
# TODO: possibly check day before and day after as well
# TODO: only allow reservations for the next x days
@bp.route('/create', methods=('POST',))
@login_required
def create():
    if request.method == 'POST':
        db = get_db()
        # Delete all pending reservations for testing / dev phase
        db.execute(
            """
            DELETE FROM reservations WHERE payment_status = 'pending'
            """
        )

        try:
            date_str = request.form['book-date'].strip()
            price = float(request.form['price'][1:3])
            discount_code = request.form.get('discountCode', None) # Returns None if key does not exist
            user = g.user['id']
        except KeyError as e:
            print(f"Missing form data: {str(e)}")
            return "Missing form data", 400

        print(f"date: {date_str}, price: {str(price)}, discount_code: {discount_code}, user: {user}")


        # Check if discount code exists
        discount_code_id = None
        if discount_code is not None:
            discount_code_id = db.execute(
                """
                SELECT id FROM discount_codes
                WHERE code = ?
                """,
                (discount_code,)
            ).fetchone()
        
        # Interpret time
        locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
        try:
            date = datetime.strptime(date_str, '%d %B %Y')
        except ValueError as e:
            # TODO: proper error handling
            print(f"Invalid date format: {str(e)}")
            return "Invalid date format", 400
        finally:
            locale.setlocale(locale.LC_TIME, 'C')
        
        # Determine start and end times.
        start = date
        end = date + timedelta(hours=22)

        try:
            cur = db.execute(
                """
                INSERT INTO reservations (renter_id, boat_id, start_time, end_time, price, discount_code_id, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user, 1, start, end, price, discount_code_id, 'pending')
            )
            db.commit()
            reservation_id = cur.lastrowid
        except Exception as e:
            print(f"Database error: {str(e)}")
            return "Database error", 500

        # Create payment in Mollie
        print(f"{get_public_url()}/webhook")
        mollie_client = get_client()
        payment = mollie_client.payments.create(
            {
                "amount": {"currency": "EUR", "value": "39.00"},
                "description": "E-Boot huren Amsterdam - " + str(date_str),
                "redirectUrl": f"{get_public_url()}/reservations/return/{reservation_id}",
                "metadata": {"payment_id": str(reservation_id)},
            }
        )

        # Add payment.id to database
        db.execute(
            """
            UPDATE reservations
            SET mollie_payment_id = ?
            WHERE id = ?
            """,
            (payment.id, reservation_id)
        )
        db.commit()
        close_db()
        return redirect(payment.checkout_url)


@bp.route('/return/<int:reservation_id>', methods=['GET'])
@login_required
def handle_return(reservation_id):
    # Get payment ID from database.
    db = get_db()

    payment_id = db.execute(
        """
        SELECT mollie_payment_id FROM reservations
        WHERE id = ?
        """,
        (reservation_id,)
    ).fetchone()['mollie_payment_id']

    payment_err = None

    if payment_id is None:
        payment_err = 'Betaling mislukt, geen betalings id gevonden. Reservering is geannuleerd'
        flash(payment_err, 'error')
        return redirect(url_for('dashboard.calendar')) 
    
    
    mollie_client = get_client()
    try:
        # Retrieve payment status from Mollie API
        mollie_payment = mollie_client.payments.get(payment_id)
    except Exception as e:
        payment_err = f'Betalingsstatus kon niet worden opgehaald. Neem contact op met de beheerder of probeer het opnieuw. Foutmelding: {str(e)}'
        flash(payment_err, 'error')
    
    # Handle payment status
    if mollie_payment.is_paid() and payment_err is None:
        try:
            # Update the payment status in database
            db.execute(
                """
                UPDATE reservations
                SET payment_status = 'paid'
                WHERE id = ?
                """,
                (reservation_id,)
            )
            db.commit()
            return redirect(url_for('reservations.my_bookings', payment_status = "success", reservation_id = reservation_id))  # Replace 'success_page' with your success page route
        except Exception as e:
            payment_err = f'Database fout: {str(e)}, reservering is niet gemaakt'
            flash(payment_err, 'error')
    
    else:
        # Log other payment statuses as needed
        if payment_err is None:
            payment_err = f'Betaling mislukt, status: {mollie_payment.status}. Reservering is geannuleerd'
        flash(payment_err, 'error')

        # Delete reservation from database
        db.execute(
            """
            DELETE FROM reservations
            WHERE id = ?
            """,
            (reservation_id,)
        )
        db.commit()
        close_db()
        return redirect(url_for('dashboard.calendar'))

@bp.route('/checkout/<int:reservation_id>', methods=['GET'])
@login_required
def checkout_page(reservation_id):
    db = get_db()
    reservation = db.execute(
        """
        SELECT start_time, price, payment_status, mollie_payment_id FROM reservations
        WHERE id = ?
        """,
        (reservation_id,)
    ).fetchone()
    
    mollie_client = get_client()
    payment_url = mollie_client.payment_links.get(reservation['mollie_payment_id'])
    print(payment_url)

    if reservation is None:
        flash('Reservation not found.', 'error')
        return redirect(url_for('index'))  # Redirect to a safe page
    
    reservation_date = reservation['start_time'].strftime('%Y-%m-%d')
    price = reservation['price']
    payment_status = reservation['payment_status']
    
    return render_template('reservations/checkout.html', reservation_date=reservation_date, price=price, payment_status=payment_status, reservation_id=reservation_id, payment_url = payment_url)


@bp.route('/get_reservations')
@login_required
def get_reservations():
    db = get_db()

    # Retrieve start and end params from the request URL
    start_date_str = request.args.get('start', '')
    end_date_str = request.args.get('end', '')

    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
    except ValueError:
        return jsonify(error="Invalid date format"), 400
    

    reservations = db.execute(
        """
        SELECT id, boat_id, renter_id, start_time, end_time FROM reservations
        WHERE start_time >= ? AND end_time <= ?
        """,
        (start_date, end_date)
    ).fetchall()

    close_db()

    # Convert events to a format suitable for FullCalendar
    reserve_list = [
        {
            "title": f"Boot reservering",
            "start": event[3].isoformat(),
            "end": event[4].isoformat(),
            "boatId": event[1],
            "renterId": event[2]
        }
        for event in reservations
    ]
    
    # Return events as JSON
    return jsonify(reserve_list)
