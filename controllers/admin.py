from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, ParkingLot, Spot, User, Reservation
from sqlalchemy.exc import IntegrityError
import matplotlib.pyplot as plt
import io
import base64

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/dashboard")
def dashboard_admin():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template("dashboard_admin.html")

@admin_bp.route("/manage_parking")
def manage_parking():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    lots = ParkingLot.query.all()
    return render_template("manage_parking.html", lots=lots)

@admin_bp.route("/add_parking", methods=["GET", "POST"])
def add_parking():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        pin_code = request.form.get("pin_code")
        price = float(request.form.get("price_per_hour"))
        max_spots = int(request.form.get("max_spots"))

        try:
            lot = ParkingLot(
                name=name,
                address=address,
                pin_code=pin_code,
                price_per_hour=price,
                max_spots=max_spots
            )
            db.session.add(lot)
            db.session.commit()

            for i in range(1, max_spots + 1):
                spot = Spot(lot_id=lot.id, spot_number=i, is_available=True)
                db.session.add(spot)

            db.session.commit()
            flash("Parking lot added successfully.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Failed to add parking lot.", "danger")

        return redirect(url_for("admin.manage_parking"))

    return render_template("add_parking.html")  # this should be a form template

@admin_bp.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    if user.email == "admin1051@gmail.com":
        flash("Cannot delete the super admin.", "danger")
        return redirect(url_for("admin.view_users"))

    try:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Failed to delete user.", "danger")

    return redirect(url_for("admin.view_users"))


@admin_bp.route('/spot_user/<int:spot_id>')
def occupied_spot_user(spot_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    spot = Spot.query.get_or_404(spot_id)

    # Get latest active reservation for this spot
    reservation = Reservation.query.filter_by(spot_id=spot.id, end_time=None).order_by(Reservation.start_time.desc()).first()

    if not reservation:
        flash("No active reservation found for this spot.", "warning")
        return redirect(url_for('admin.view_spots', lot_id=spot.lot_id))

    user = User.query.get(reservation.user_id)
    return render_template("spot_user_details.html", user=user, reservation=reservation, spot=spot)


@admin_bp.route("/edit_parking/<int:lot_id>", methods=["GET", "POST"])
def edit_parking(lot_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == "POST":
        lot.name = request.form.get("name")
        lot.address = request.form.get("address")
        lot.pin_code = request.form.get("pin_code")
        
        price_input = request.form.get("price_per_hour")
        max_spots_input = request.form.get("max_spots")

        if not price_input or not max_spots_input:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin.edit_parking", lot_id=lot.id))

        try:
            lot.price_per_hour = float(price_input)
            new_max_spots = int(max_spots_input)

            current_spots = Spot.query.filter_by(lot_id=lot.id).count()
            lot.max_spots = new_max_spots

            if new_max_spots > current_spots:
                for i in range(current_spots + 1, new_max_spots + 1):
                    db.session.add(Spot(lot_id=lot.id, spot_number=i, is_available=True))
            elif new_max_spots < current_spots:
                extra_spots = Spot.query.filter_by(lot_id=lot.id, is_available=True).order_by(Spot.spot_number.desc()).limit(current_spots - new_max_spots).all()
                for spot in extra_spots:
                    db.session.delete(spot)

            db.session.commit()
            flash("Parking lot updated.", "success")
            return redirect(url_for("admin.manage_parking"))
        
        except ValueError:
            flash("Invalid numeric input for price or spots.", "danger")
            return redirect(url_for("admin.edit_parking", lot_id=lot.id))

    return render_template("edit_parking.html", lot=lot)

@admin_bp.route("/delete_parking/<int:lot_id>")
def delete_parking(lot_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    try:
        db.session.delete(lot)
        db.session.commit()
        flash("Parking lot deleted successfully.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Cannot delete parking lot with existing references.", "danger")

    return redirect(url_for("admin.manage_parking"))

@admin_bp.route("/view_spots/<int:lot_id>")
def view_spots(lot_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    spots = Spot.query.filter_by(lot_id=lot.id).order_by(Spot.spot_number).all()
    return render_template("view_spots.html", lot=lot, spots=spots)

@admin_bp.route("/delete_spot/<int:spot_id>")
def delete_spot(spot_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    spot = Spot.query.get_or_404(spot_id)
    lot = spot.lot

    if not spot.is_available:
        flash("Cannot delete an occupied spot.", "danger")
    else:
        db.session.delete(spot)
        db.session.commit()
        lot.max_spots -= 1
        db.session.commit()
        flash("Spot deleted and spot numbers updated.", "success")

    return redirect(url_for("admin.view_spots", lot_id=lot.id))

@admin_bp.route("/search", methods=["GET"])
def admin_search():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    filter_by = request.args.get('filter_by')
    query = request.args.get('query', '').strip()

    if not query or not filter_by:
        return render_template("admin_search.html")

    results_users = []
    results_lots = []

    # User-based filters
    if filter_by == "user_name":
        results_users = User.query.filter(User.full_name.ilike(f"%{query}%")).all()
    elif filter_by == "user_email":
        results_users = User.query.filter(User.email.ilike(f"%{query}%")).all()
    elif filter_by == "user_phone":
        results_users = User.query.filter(User.phone.ilike(f"%{query}%")).all()
    
    # Parking lot-based filters
    elif filter_by == "lot_name":
        results_lots = ParkingLot.query.filter(ParkingLot.name.ilike(f"%{query}%")).all()
    elif filter_by == "lot_address":
        results_lots = ParkingLot.query.filter(ParkingLot.address.ilike(f"%{query}%")).all()
    
    # Combined pin code filter (search both User and Lot pin codes)
    elif filter_by == "pin_code":
        results_users = User.query.filter(User.pin_code.ilike(f"%{query}%")).all()
        results_lots = ParkingLot.query.filter(ParkingLot.pin_code.ilike(f"%{query}%")).all()

    return render_template(
        "admin_search_results.html",
        query=query,
        users=results_users,
        lots=results_lots
    )

 
@admin_bp.route("/view_users")
def view_users():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    users = User.query.filter(User.email != "admin1051@gmail.com").all()
    return render_template("view_users.html", users=users)

@admin_bp.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.full_name = request.form.get("name")
        user.address = request.form.get("address")
        user.pin_code = request.form.get("pin_code")
        user.phone = request.form.get("phone")
        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for("admin.view_users"))

    return render_template("edit_user.html", user=user)

@admin_bp.route("/summary")
def admin_summary():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    from models import ParkingLot, Reservation, User
    lots = ParkingLot.query.all()

    # Data: {lot_name: {user_name: revenue, ...}, ...}
    stacked_data = {}

    for lot in lots:
        lot_name = lot.name or f"Lot {lot.id}"
        stacked_data[lot_name] = {}
        reservations = Reservation.query.filter_by(lot_id=lot.id).all()

        for res in reservations:
            if res.user_id and res.end_time and res.start_time:
                user = User.query.get(res.user_id)
                if user:
                    hours = (res.end_time - res.start_time).total_seconds() / 3600
                    user_name = user.full_name or f"User {user.id}"
                    revenue = round(hours * (lot.price_per_hour or 0), 2)
                    stacked_data[lot_name][user_name] = stacked_data[lot_name].get(user_name, 0) + revenue

    # Prepare plot data
    lot_names = list(stacked_data.keys())
    users_set = set()
    for user_revenues in stacked_data.values():
        users_set.update(user_revenues.keys())
    user_names = sorted(users_set)

    # Construct matrix: each row per user across all lots
    revenue_matrix = []
    for user in user_names:
        row = [stacked_data[lot].get(user, 0) for lot in lot_names]
        revenue_matrix.append(row)

    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bottoms = [0] * len(lot_names)
    colors = plt.cm.tab20.colors

    for i, user in enumerate(user_names):
        revenues = revenue_matrix[i]
        ax.bar(lot_names, revenues, bottom=bottoms, label=user, color=colors[i % len(colors)])
        bottoms = [bottoms[j] + revenues[j] for j in range(len(lot_names))]

    ax.set_title('Total Revenue per Lot (Stacked by User)')
    ax.set_xlabel('Parking Lot')
    ax.set_ylabel('Revenue (₹)')
    ax.legend(fontsize='small', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert chart to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_url = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    return render_template("admin_summary.html", bar_graph=chart_url)

