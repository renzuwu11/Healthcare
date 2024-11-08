from flask import Flask, render_template, redirect, session, url_for, flash, request
import psycopg2
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Database connection function
def get_db_connection():
    try:
        authdb = psycopg2.connect(
            host=os.getenv("AUTH_DB_HOST"),
            user=os.getenv("AUTH_DB_USER"),
            password=os.getenv("AUTH_DB_PASSWORD"),
            dbname=os.getenv("AUTH_DB_NAME"),
            sslmode='require'
        )
        print("Database connection established successfully.")
        return authdb
    except psycopg2.OperationalError as e:
        print(f"OperationalError: {e}")
    except psycopg2.DatabaseError as e:
        print(f"DatabaseError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

# Redirect users to the authentication microservice login page
@app.route('/login')
def login_page():
    auth_url = 'https://authentication-microservice-3wvv.onrender.com'
    print(f"Redirecting to authentication service: {auth_url}")  # Debugging log
    return redirect(auth_url)


# Handle the callback from the authentication microservice
@app.route('/auth/callback')
def auth_callback():
    # Assume authentication microservice sends the user token or data via query params
    token = request.args.get('token')
    print(f"Token received in callback: {token}")  # Debugging log
    
    if token:
        # Optionally verify the token if needed (e.g., by making a request to the auth service)
        session['token'] = token
        print(f"Token stored in session: {session['token']}")  # Debugging log
        
        # Now fetch the user details (e.g., username, role) from the token or through another API call
        user_data_url = f'https://authentication-microservice-3wvv.onrender.com/user/{token}'
        print(f"Fetching user data from: {user_data_url}")  # Debugging log
        response = requests.get(user_data_url)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"User data fetched: {user_data}")  # Debugging log
            session['username'] = user_data['username']
            session['role'] = user_data['role']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to the main dashboard or home page
        else:
            print(f"Error fetching user data: {response.status_code} - {response.text}")  # Debugging log
            flash('Invalid session or token.', 'danger')
            return redirect(url_for('login_page'))  # Redirect to the login page

    print("No token received. Authentication failed.")  # Debugging log
    flash('Authentication failed. Please try again.', 'danger')
    return redirect(url_for('login_page'))

@app.route('/admin-dashboard')
def admin_dashboard():
    # Ensure user is logged in and is an admin
    if 'username' not in session or session.get('role') != 'System Admin':
        flash('You do not have access to this page. Please log in as an admin.', 'warning')
        return redirect(url_for('login_page'))
    return render_template('admin_dashboard.html', username=session.get('username'), role=session.get('role'))

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
    return redirect(url_for('login_page'))  # Redirect to the login page

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
