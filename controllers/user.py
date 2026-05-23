from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import db, ParkingLot, Spot, Reservation, User
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    lots = ParkingLot.query.all()
    active = Reservation.query.filter_by(user_id=user_id, end_time=None).first()
    
    return render_template('dashboard_user.html', lots=lots, active=active, user=user)


@user_bp.route('/summary')
def user_summary():
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    lots = ParkingLot.query.all()
    lot_names = []
    vacant_counts = []
    occupied_counts = []

    for lot in lots:
        lot_name = lot.name or f"Lot {lot.id}"
        lot_names.append(lot_name)
        vacant = Spot.query.filter_by(lot_id=lot.id, is_available=True).count()
        occupied = Spot.query.filter_by(lot_id=lot.id, is_available=False).count()
        vacant_counts.append(vacant)
        occupied_counts.append(occupied)

    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bar1 = ax.bar(lot_names, vacant_counts, label='Vacant', color='green')
    bar2 = ax.bar(lot_names, occupied_counts, bottom=vacant_counts, label='Occupied', color='red')

    ax.set_title('Vacant vs Occupied Spots per Parking Lot')
    ax.set_xlabel('Parking Lot')
    ax.set_ylabel('Number of Spots')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_url = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    return render_template("user_summary.html", chart=chart_url)


@user_bp.route('/available')
def view_available_parking():
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    lots = ParkingLot.query.all()
    return render_template('available_parking.html', lots=lots)


@user_bp.route('/book/<int:lot_id>', methods=["GET", "POST"])
def book(lot_id):
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    lot = ParkingLot.query.get_or_404(lot_id)
    available_spot = Spot.query.filter_by(lot_id=lot_id, is_available=True).first()

    if not available_spot:
        flash("No spots available at this moment.", "danger")
        return redirect(url_for('user.user_dashboard'))

    if request.method == "POST":
        vehicle_number = request.form.get("vehicle_number")

        available_spot.is_available = False
        reservation = Reservation(
            user_id=user_id,
            lot_id=lot.id,
            spot_id=available_spot.id,
            vehicle_number=vehicle_number,
            start_time=datetime.now(),
            status="active",
        )
        db.session.add(reservation)
        db.session.commit()
        flash("Spot successfully booked.", "success")
        return redirect(url_for('user.user_dashboard'))

    return render_template("confirm_booking.html", lot=lot, spot=available_spot, user_id=user_id)


@user_bp.route('/active')
def active_reservations():
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    active = Reservation.query.filter_by(user_id=user_id, end_time=None).all()
    return render_template('active_reservations.html', active=active)


@user_bp.route('/vacate/<int:reservation_id>', methods=["POST"])
def vacate_reservation(reservation_id):
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.end_time:
        flash("Reservation already completed.", "warning")
        return redirect(url_for('user.active_reservations'))

    end_time = datetime.now()
    duration_minutes = (end_time - reservation.start_time).total_seconds() / 60
    cost_per_minute = reservation.lot.price_per_hour / 60
    cost = round(duration_minutes * cost_per_minute, 2)

    reservation.end_time = end_time
    reservation.status = 'completed'
    reservation.cost = cost
    reservation.spot.is_available = True

    db.session.commit()
    flash(f"Spot vacated. Total cost: ₹{cost}", "info")
    return redirect(url_for('user.active_reservations'))

@user_bp.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.full_name = request.form.get("name")
        user.address = request.form.get("address")
        user.pin_code = request.form.get("pin_code")
        user.phone = request.form.get("phone")

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("user.user_dashboard"))

    return render_template("edit_profile_user.html", user=user)


@user_bp.route("/history")
def reservation_history():
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    return render_template("reservation_history.html", reservations=reservations)

