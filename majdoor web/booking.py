from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required
from app import mysql  # Adjust according to your app structure

# Create a Blueprint for booking routes
booking_routes = Blueprint('booking_routes', __name__)


@booking_routes.route('/book_carpenter', methods=['GET', 'POST'])
@login_required
def book_carpenter():
    if request.method == "POST":
        # Get data from the form
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        street = request.form.get('street')
        description = request.form.get('message')
        date_of_booking = request.form.get('dob')  # Assuming date of booking is in the form
        full_name = f"{first_name.capitalize()} {last_name.capitalize()}"
        full_address = f"{address} {street} {pincode}"
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()

        # Correct SQL query to insert data into the booking table
        query = """
            INSERT INTO booking (user_id, full_name, phone_number, email, description, address, booking_type, date_of_booking)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query,
                       (user_id, full_name, phone, email, description, full_address, "carpenter", date_of_booking))

        # Commit the transaction
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('dashboard'))

    return render_template('form.html')


# Route for booking shifting
@booking_routes.route('/shifting', methods=['GET', 'POST'])
@login_required
def shifting():
    if request.method == "POST":
        # Get data from the form
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        street = request.form.get('street')
        description = request.form.get('message')
        date_of_booking = request.form.get('dob')  # Assuming date of booking is in the form

        full_name = f"{first_name.capitalize()} {last_name.capitalize()}"
        full_address = f"{address} {street} {pincode}"
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()

        # Correct SQL query to insert data into the booking table
        query = """
            INSERT INTO booking (user_id, full_name, phone_number, email, description, address, booking_type, date_of_booking)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
        user_id, full_name, phone, email, description, full_address, "Lifting/shifting", date_of_booking))

        # Commit the transaction
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('dashboard'))

    return render_template('form.html')
