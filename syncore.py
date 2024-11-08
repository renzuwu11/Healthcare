from flask import Flask, render_template, redirect, session, url_for, flash, request
import psycopg2, requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Database connection function
def authdb():
    try:
        # Attempt to connect to the database
        authdb = psycopg2.connect(
            host=os.getenv("AUTH_DB_HOST"),
            user=os.getenv("AUTH_DB_USER"),
            password=os.getenv("AUTH_DB_PASSWORD"),
            dbname=os.getenv("AUTH_DB_NAME"),
            sslmode='require'
        )
        auth_cursor = authdb.cursor()
        print("Successfully connected to the authentication database.")
        return authdb, auth_cursor  # Return both the connection and cursor
    except psycopg2.OperationalError as e:
        # Handle operational errors like connection issues
        print(f"OperationalError: {e}")
        return None, None
    except psycopg2.InterfaceError as e:
        # Handle interface errors like configuration issues
        print(f"InterfaceError: {e}")
        return None, None
    except psycopg2.Error as e:
        # General error handler for any other psycopg2 errors
        print(f"Error connecting to the authentication database: {e}")
        return None, None

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    # Use the deployed authentication microservice URL
    url = "https://authentication-microservice-1-ux4a.onrender.com/authenticate"
    data = {
        "username": username,
        "password": password,
    }
    headers = {
        "Content-Type": "application/json",
    }

    # Check if the account is locked
    account_locked_response = requests.get(f"https://authentication-microservice-1-ux4a.onrender.com/checkAccountLocked/{username}")
    if account_locked_response.status_code == 200 and account_locked_response.json().get("locked"):
        flash("Your account is now locked, please contact tech support.")
        return redirect(url_for('login'))

    # Authenticate user
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        session['loginAttempts'] = 0
        token = response.json().get('token')

        # Verify token
        verify_url = "https://authentication-microservice-1-ux4a.onrender.com/verify-token"
        verify_response = requests.post(verify_url, json={'token': token}, headers=headers)

        if verify_response.status_code == 200:
            user_data = verify_response.json()
            session['username'] = user_data['username']
            session['role'] = user_data['role']
            return redirect(url_for('dash_finance'))
        else:
            flash('Token verification failed.')
            return redirect(url_for('login'))

    elif response.status_code == 401:
        if 'loginAttempts' not in session:
            session['loginAttempts'] = 0
        session['loginAttempts'] += 1

        if session['loginAttempts'] >= 3:
            flash("Invalid credentials. You have made 3 unsuccessful attempts. Your account is now locked. Please contact tech support.")
            requests.post("https://authentication-microservice-1-ux4a.onrender.com/accountLocked", json={"username": username}, headers=headers)
        else:
            flash('Invalid credentials. Your account will be locked after multiple unsuccessful attempts.')

        return redirect(url_for('login'))

    elif response.status_code in [400, 403]:
        flash('Invalid credentials or access denied. Please check your username and password.')
        return redirect(url_for('login'))

    else:
        flash(f'Unexpected error occurred: {response.status_code}. Please try again later or contact tech support.')
        return redirect(url_for('login'))

@app.route('/admin-dashboard')
def admin_dashboard():
    # Ensure the user is logged in by checking for the token in the session
    if 'token' not in session:
        print("No token found in session.")  # Debugging
        flash('You do not have access to this page. Please log in.', 'warning')
        return redirect(url_for('login_page'))
    
    print("Token found in session, granting access.")  # Debugging
    return render_template('admin_dashboard.html')

@app.route('/fms')
def fms():
    # Ensure user is logged in and has the appropriate role
    if 'username' not in session or session.get('role') not in ['Finance Manager', 'Billing Specialist', 'Claims Specialist']:
        flash('You do not have access to this page.', 'warning')
        return redirect(url_for('login_page'))
    return render_template('fms.html', username=session.get('username'), role=session.get('role'))

@app.route('/pms')
def pms():
    # Ensure user is logged in and has the appropriate role
    if 'username' not in session or session.get('role') != 'PMS Admin':
        flash('You do not have access to this page.', 'warning')
        return redirect(url_for('login_page'))
    return render_template('pms.html', username=session.get('username'), role=session.get('role'))

@app.route('/lms')
def lms():
    # Ensure user is logged in and has the appropriate role
    if 'username' not in session or session.get('role') != 'LMS Admin':
        flash('You do not have access to this page.', 'warning')
        return redirect(url_for('login_page'))
    return render_template('lms.html', username=session.get('username'), role=session.get('role'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('token', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_page'))

@app.route('/')
def index():
    # Redirect to the landing page with buttons
    return render_template('redirect.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
