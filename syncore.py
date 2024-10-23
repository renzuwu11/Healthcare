from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection setup
def get_db_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="fms-group3",
            database="authentication"
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Define role access conditions
ROLE_ACCESS = {
    'Finance Manager': 'fms',
    'Billing Specialist': 'fms',
    'Claims Specialist': 'fms',
    'Medical Staff': 'pms',
    'Doctor': 'pms',
    'Patient': 'pms',
    'PMS Admin': 'pms',
    'LMS Admin': 'lms',
    'Hospital Staff': 'lms',
    'System Admin': 'admin-dashboard'  # Ensure the system admin role is included
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/login')
def login():
    # Prioritize the system from the query parameter, fall back on session value
    system = request.args.get('system') or session.get('requested_system')
    if system:
        session['requested_system'] = system  # Store system in session if it exists
    return render_template('login.html', system=system)  # Pass system to login template

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    system = request.form.get('system') or session.get('requested_system')  # Retrieve system from form or session

    authdb = get_db_connection()
    if not authdb:
        flash("Database connection error.")
        return redirect(url_for('login', system=system))

    authcursor = authdb.cursor()

    try:
        # Store the requested system in the session
        session['requested_system'] = system  # Store it in session

        # Check if the account is locked
        authcursor.execute("SELECT accountLocked FROM USERS WHERE username = %s", (username,))
        account_locked_result = authcursor.fetchone()

        if account_locked_result and account_locked_result[0]:
            flash("Your account is locked. Please contact tech support.")
            return redirect(url_for('login', system=system))

        # Perform authentication
        url = "http://localhost:10000/authenticate"  # Updated to port 10000
        data = {"username": username, "password": password}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            session['loginAttempts'] = 0
            token = response.json().get('token')
            verify_url = "http://localhost:10000/verify-token"  # Updated to port 10000
            verify_response = requests.post(verify_url, json={'token': token}, headers=headers)

            if verify_response.status_code == 200:
                user_data = verify_response.json()
                session['username'] = user_data['username']
                session['role'] = user_data['role']

                # Debug prints to check role and system
                print(f"User Role: {session['role']}")
                print(f"Requested System from session: {session.get('requested_system')}")

                # Check if the user role is allowed to access the requested system
                if session['role'] in ROLE_ACCESS and ROLE_ACCESS[session['role']] == session.get('requested_system'):
                    # Define role-based redirect URLs
                    role_redirects = {
                        'Finance Manager': "https://finance-1qfw.onrender.com/dash_finance",
                        'Billing Specialist': "https://finance-1qfw.onrender.com/dash_finance",
                        'Claims Specialist': "https://finance-1qfw.onrender.com/dash_finance",
                        'PMS Admin': "https://hms-ui-gv0l.onrender.com/admin_med/layout/emergency_records.html",
                        'LMS Admin': "https://hospital-logistics.onrender.com",
                        'System Admin': url_for('admin_dashboard')  # Redirect to admin dashboard
                    }

                    redirect_url = role_redirects.get(session['role'])
                    if redirect_url:
                        return redirect(redirect_url)
                else:
                    flash("You do not have access to this system.")
                    return redirect(url_for('login', system=system))

            else:
                flash('Token verification failed.')
                return redirect(url_for('login', system=system))

        elif response.status_code == 401:
            if 'loginAttempts' not in session:
                session['loginAttempts'] = 0
            session['loginAttempts'] += 1

            if session['loginAttempts'] >= 3:
                flash("Invalid credentials. Your account is now locked. Please contact tech support.")
                authcursor.execute("UPDATE USERS SET accountLocked = TRUE WHERE username = %s", (username,))
                authdb.commit()
            else:
                flash('Invalid credentials. Your account will be locked after multiple unsuccessful attempts.')

            # Redirect and ensure system is still passed
            return redirect(url_for('login', system=system))

        elif response.status_code in [400, 403]:
            flash('Invalid credentials or access denied. Please check your username and password.')
            return redirect(url_for('login', system=system))
        else:
            flash(f'Unexpected error occurred: {response.status_code}. Please try again later.')
            return redirect(url_for('login', system=system))
    except Exception as e:
        flash(f'An error occurred: {e}')
        return redirect(url_for('login', system=system))
    finally:
        authcursor.close()
        authdb.close()

@app.route('/fms')
def fms():
    return render_template('fms.html')

@app.route('/pms')
def pms():
    return render_template('pms.html')

@app.route('/lms')
def lms():
    return render_template('lms.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
