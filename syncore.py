from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2, requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

@app.route('/')
def index():
    return render_template('redirect.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/forgot-password')
def forgot_pass():
    return render_template('forgot_pass.html')

@app.route('/tech-support')
def tech_support():
    return render_template('tech_support.html')

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
            return redirect(url_for('admin_dashboard'))
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
    return render_template('admin_dashboard.html')

@app.route('/fms')
def fms():
    authdb = get_db_connection()
    if not authdb:
        flash("Database connection error.")
        return redirect(url_for('index'))

    authcursor = authdb.cursor()
    try:
        # Fetch users with roles specific to FMS (Finance Manager, Billing Specialist, Claims Specialist)
        query = """
        SELECT u.username, a.roleName, u.accountLocked 
        FROM USERS u
        JOIN AUTHORIZATIONS a ON u.authorizationId = a.authorizationId
        WHERE a.roleName IN ('Finance Manager', 'Billing Specialist', 'Claims Specialist')
        """
        authcursor.execute(query)
        users = authcursor.fetchall()  # Get the filtered users

        # Format the data as a list of dictionaries
        users_data = []
        for user in users:
            users_data.append({
                'username': user[0],
                'role': user[1],
                'status': 'Active' if not user[2] else 'Inactive'
            })

        return render_template('fms.html', users=users_data)
    except Exception as e:
        flash(f'An error occurred: {e}')
        return redirect(url_for('redirect'))
    finally:
        authcursor.close()
        authdb.close()

@app.route('/pms')
def pms():
    return render_template('pms.html')

@app.route('/lms')
def lms():
    return render_template('lms.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
