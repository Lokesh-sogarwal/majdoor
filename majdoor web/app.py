import MySQLdb
from flask import Flask, render_template, flash, redirect, url_for, session,request
from flask_mysqldb import MySQL
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
import random
from flask_mail import Mail, Message
from functools import wraps
from datetime import datetime, timedelta


####################################################################################################################################
##################################    Configuration    #############################################################################
####################################################################################################################################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'majdoorindia'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Or use another mail service
app.config['MAIL_PORT'] = 587  # Typically 587 for TLS
app.config['MAIL_USE_TLS'] = True  # Set to True for TLS
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'noreply.educonnect551@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = "hivz kuvf zkeq yobg"  # Replace with your email password or app password
app.config['MAIL_DEFAULT_SENDER'] = 'noreply.educonnect551@gmail.com'  # Set a default sender email

mail=Mail(app)
mysql = MySQL(app)

####################################################################################################################################
##################################    OTP Generation   .....................................
####################################################################################################################################
def generate_otp():
    return random.randint(100000, 999999)
####################################################################################################################################
##################################    Sending mails  .....................................
####################################################################################################################################
def send_email(subject, recipient, body):
    try:
        msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
        msg.body = body
        mail.send(msg)
        flash(f'Email sent to {recipient}', 'success')
    except Exception as e:
        flash(f'Failed to send email: {str(e)}', 'error')

####################################################################################################################################
##################################    Login status  .....................................
####################################################################################################################################

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to login first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

####################################################################################################################################
##################################    Home page .....................................
####################################################################################################################################

@app.route("/")
def home():
    return render_template("index.html")


####################################################################################################################################
##################################    For Registration .....................................
####################################################################################################################################

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user_id = random.randint(10000, 99999)
            first_name = form.first_name.data.capitalize()
            last_name = form.last_name.data.capitalize()
            phone_no = form.phone_no.data
            email = form.email.data.lower()
            password = form.password.data
            confirm_password = form.confirm_password.data

            # Check if passwords match
            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template("register.html", form=form)

            # Check if email or phone number is already registered
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s OR phone_number = %s", (email, phone_no))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("Email or phone number already registered.", "error")
                return render_template("register.html", form=form)


            hashed_password = generate_password_hash(password)
            otp = generate_otp()
            session['otp'] = otp
            session['otp_timestamp'] = datetime.now().timestamp()

            session['temp_user_details'] = {
                'user_id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': hashed_password,
                'role': 'user',
                'phone_number': phone_no
            }
            session['email'] = email
            # Send OTP to the user's email
            send_email('OTP Verification', email, f'Your OTP for verification is {otp}. Please do not share this with anyone.')

            flash('Please verify your email address using the OTP sent to your email.', 'success')

        # Redirect to OTP verification page
            return redirect(url_for('otp', email=email))

        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'error')

    return render_template("register.html", form=form)


####################################################################################################################################
##################################    For Verify the otp .....................................
####################################################################################################################################

@app.route("/otp", methods=['GET', 'POST'])
def otp():
    if request.method == "POST":
        actual_otp = session.get('otp')
        v1 = request.form.get('first')
        v2 = request.form.get('second')
        v3 = request.form.get('third')
        v4 = request.form.get('fourth')
        v5 = request.form.get('fifth')
        v6 = request.form.get('sixth')
        entered_otp = f"{v1}{v2}{v3}{v4}{v5}{v6}"
        # Compare the OTPs
        if int(entered_otp) == int(actual_otp):
            user_details = session.pop('temp_user_details', None)
            if user_details:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    "INSERT INTO users (first_name, last_name, email, password, role, phone_number) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_details['first_name'], user_details['last_name'], user_details['email'],
                      user_details['password'], user_details['role'], user_details['phone_number'])
                )
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('login'))
        else:
            return "Invalid OTP", 401  # Return an error if OTPs don't match

    # GET method: Render the OTP page
    email = session.get('email')
    return render_template("otp.html", email=email)

####################################################################################################################################
########################################    For resending the otp ..................................................................
####################################################################################################################################

@app.route("/resend", methods=['POST', 'GET'])
def resend():
    email = session.get('email')  # Get email from the session
    if not email:
        flash("No email address found in session. Please restart the process.")
        return redirect(url_for('register'))  # Redirect to a safe route

    otp = generate_otp()  # Generate a new OTP
    session['otp'] = otp
    session['otp_timestamp'] = datetime.now().timestamp()
    send_email(
        'OTP Verification',
        email,
        f'Your OTP for verification is {otp}. Please do not share this with anyone.'
    )
    flash("A new OTP has been sent to your email.")
    return render_template('otp.html', email=email)


####################################################################################################################################
##################################    For Login logic .....................................
####################################################################################################################################

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                session['role'] = user['role']
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'error')
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
        finally:
            cursor.close()

    return render_template('login.html', form=form)


####################################################################################################################################
##################################    Logout Logic .....................................
####################################################################################################################################@app.route('/logout')
@app.route("/logout",methods=['GET','POST'])
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

####################################################################################################################################
##################################    Dashboard Logic.....................................
####################################################################################################################################

@app.route("/dashboard")
@login_required
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for('login'))

    email = session.get('email')
    print("Session email during dashboard access:", email)  # Debugging

    if not email:
        flash("User email not found in session.", "error")
        return redirect(url_for('login'))

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        print("User data fetched from database:", user)  # Debugging

        if user:
            role = user.get('role')
            if role == 'employee':
                return render_template('employeedashboard.html',role=role)
            if role == 'admin':
                
                return render_template('admindashboard.html', role=role)
            elif role == 'user':
            
                return render_template('dashboard.html', role=role)
            else:
                flash("Unknown role", "error")
                return redirect(url_for('login'))
        else:
            flash("User not found in the database.", "error")
            return redirect(url_for('login'))

    except Exception as e:
        flash("An error occurred while accessing the dashboard. Please try again.", "error")
        print(f"Error: {e}")  # Debugging
        return redirect(url_for('login'))
    
####################################################################################################################################
##################################    Booking a carpenter  .....................................
####################################################################################################################################

@app.route('/book_carpenter', methods=['GET', 'POST'])
@login_required
def book_carpenter():
    if request.method == "POST":
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        street = request.form.get('street')
        description = request.form.get('message')
        date_of_booking = request.form.get('dob')  # Assuming date of booking is in the form
        full_name = str(first_name.capitalize() + " " + last_name.capitalize())
        full_address = str(address) + " " + str(street) + " " + str(pincode)
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()

        # Correct SQL query to insert data into booking table
        query = """
            INSERT INTO booking (user_id, full_name, phone_number, email, description, address, booking_type, date_of_booking)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Ensure the arguments are in a tuple
        cursor.execute(query,
                       (user_id, full_name, phone, email, description, full_address, "carpenter", date_of_booking))

        # Commit the transaction
        mysql.connection.commit()

        # Close the cursor
        cursor.close()

        return redirect(url_for('success.html'))

    return render_template('formcar.html')

####################################################################################################################################
##################################    Booking a shifter  .....................................
####################################################################################################################################

@ app.route('/shifting', methods=['GET', 'POST'])
@ login_required
def shifting():
    if request.method == "POST":
        # Get data from the form
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = str(request.form.get('address'))
        pincode = str(request.form.get('pincode'))
        street = str(request.form.get('street'))
        description = request.form.get('message')
        date_of_booking = request.form.get('dob')  # Assuming date of booking is in the form

        # Format the full name and address
        full_name = f"{first_name.capitalize()} {last_name.capitalize()}"
        full_address = f"{address} {street} {pincode}"

        # Get the user_id from session
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()

        # Correct SQL query to insert data into the booking table
        query = """
            INSERT INTO booking (user_id, full_name, phone_number, email, description, address, booking_type, date_of_booking)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Ensure the arguments are passed correctly as a tuple
        cursor.execute(query,
                       (user_id, full_name, phone, email, description, full_address, "Lifting/shifting", date_of_booking))

        # Commit the transaction
        mysql.connection.commit()

        # Close the cursor
        cursor.close()

        # Redirect to the dashboard or another appropriate page
        return render_template('success.html')

    return render_template('formlift.html')

####################################################################################################################################
##################################    Booking a tutor  .....................................
####################################################################################################################################

@app.route('/tutor', methods=['GET', 'POST'])
@login_required
def tutor():
    if request.method == "POST":
        # Get data from the form
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = str(request.form.get('address'))
        pincode = str(request.form.get('pincode'))
        street = str(request.form.get('street'))
        description = request.form.get('message')
        date_of_booking = request.form.get('dob')  # Assuming date of booking is in the form

        # Format the full name and address
        full_name = f"{first_name.capitalize()} {last_name.capitalize()}"
        full_address = f"{address} {street} {pincode}"

        # Get the user_id from session
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()

        # Correct SQL query to insert data into the booking table
        query = """
            INSERT INTO booking (user_id, full_name, phone_number, email, description, address, booking_type, date_of_booking)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Ensure the arguments are passed correctly as a tuple
        cursor.execute(query,
                       (user_id, full_name, phone, email, description, full_address, "Tutor", date_of_booking))

        # Commit the transaction
        mysql.connection.commit()

        # Close the cursor
        cursor.close()

        # Redirect to the dashboard or another appropriate page
        return render_template('success.html')

    return (render_template('formtut.html'))

####################################################################################################################################
##################################    Booking a tutor  .....................................
####################################################################################################################################

@app.route('/book_elec', methods=['GET', 'POST'])
@login_required
def elec():
    if request.method == "POST":
        # Get data from the form
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = str(request.form.get('address'))
        pincode = str(request.form.get('pincode'))
        street = str(request.form.get('street'))
        description = request.form.get('message')
        date_of_booking = request.form.get('dob')  # Assuming date of booking is in the form

        # Format the full name and address
        full_name = f"{first_name.capitalize()} {last_name.capitalize()}"
        full_address = f"{address} {street} {pincode}"

        # Get the user_id from session
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()

        # Correct SQL query to insert data into the booking table
        query = """
            INSERT INTO booking (user_id, full_name, phone_number, email, description, address, booking_type, date_of_booking)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Ensure the arguments are passed correctly as a tuple
        cursor.execute(query,
                       (user_id, full_name, phone, email, description, full_address, "Electrician", date_of_booking))

        # Commit the transaction
        mysql.connection.commit()

        # Close the cursor
        cursor.close()

        # Redirect to the dashboard or another appropriate page
        return render_template('success.html')

    return render_template('formelec.html')



####################################################################################################################################
##################################    Booking a tutor  .....................................
####################################################################################################################################

@app.route('/carwash', methods=['GET', 'POST'])
@login_required
def carwash():
    if request.method == "POST":
        # Get data from the form
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = str(request.form.get('address'))
        pincode = str(request.form.get('pincode'))
        street = str(request.form.get('street'))
        description = request.form.get('message')
        date_of_booking = request.form.get('dob')  # Assuming date of booking is in the form

        # Format the full name and address
        full_name = f"{first_name.capitalize()} {last_name.capitalize()}"
        full_address = f"{address} {street} {pincode}"

        # Get the user_id from session
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()

        # Correct SQL query to insert data into the booking table
        query = """
            INSERT INTO booking (user_id, full_name, phone_number, email, description, address, booking_type, date_of_booking)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Ensure the arguments are passed correctly as a tuple
        cursor.execute(query,
                       (user_id, full_name, phone, email, description, full_address, "Carwash", date_of_booking))

        # Commit the transaction
        mysql.connection.commit()

        # Close the cursor
        cursor.close()

        # Redirect to the dashboard or another appropriate page
        return render_template('success.html')

    return render_template('formcarwash.html')


if __name__ == '__main__':
    app.run(debug=True)
