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
def index():
    # Redirect to the landing page with buttons
    return render_template('redirect.html')

@app.route('/syncore-login')
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
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', username=session['username'], role=session['role']) 

@app.route('/fms')
def fms():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms.html', username=session['username'], role=session['role']) 

@app.route('/pms')
def pms():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('pms.html', username=session['username'], role=session['role']) 


@app.route('/lms')
def lms():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('lms.html', username=session['username'], role=session['role']) 

# Route for the Emergency Patients page
@app.route('/emergency_patients')
def emergency_patients():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('emergency_patients.html', username=session['username'], role=session['role']) 


# Logistics Management System

# Route for the Logistics Dashboard
@app.route('/lms_dashboard')
def lms_dashboard():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('lms_dashboard.html', username=session['username'], role=session['role'])

# Route for the Suppliers page
@app.route('/lms_suppliers')
def lms_suppliers():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('lms_suppliers.html', username=session['username'], role=session['role'])

# Route for the Requisition page
@app.route('/lms_requisition')
def lms_requisition():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('lms_requisition.html', username=session['username'], role=session['role'])

# Route for the Purchase Order page
@app.route('/lms_purchase_order')
def lms_purchase_order():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('lms_purchase_order.html', username=session['username'], role=session['role'])

# Route for the Inventory page
@app.route('/lms_inventory')
def lms_inventory():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('lms_inventory.html', username=session['username'], role=session['role'])

# Route for the Signatory page
@app.route('/lms_signatory')
def lms_signatory():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('lms_signatory.html', username=session['username'], role=session['role'])

# Finance Management System

# Route for Finance Manager Dashboard
@app.route('/fms_dashboard_finance_manager')
def fms_dashboard_finance_manager():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_fm_dashboard.html', username=session['username'], role=session['role'])

# Route for Billing Specialist Dashboard
@app.route('/fms_dashboard_billing_specialist')
def fms_dashboard_billing_specialist():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_bs_dashboard.html', username=session['username'], role=session['role'])

# Route for Claims Specialist Dashboard
@app.route('/fms_dashboard_claims_specialist')
def fms_dashboard_claims_specialist():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_cs_dashboard.html', username=session['username'], role=session['role'])

# Route for Employees page
@app.route('/fms_employees')
def fms_employees():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_employees.html', username=session['username'], role=session['role'])

# Route for Services page
@app.route('/fms_services')
def fms_services():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_services.html', username=session['username'], role=session['role'])

# Route for Medical Ward page
@app.route('/fms_medical_ward')
def fms_medical_ward():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_medical_ward.html', username=session['username'], role=session['role'])

# Route for Radiology Ward page
@app.route('/fms_radiology_ward')
def fms_radiology_ward():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_radiology_ward.html', username=session['username'], role=session['role'])

# Route for Hospital Patients page
@app.route('/fms_hospital_patients')
def fms_hospital_patients():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_hospital_patients.html', username=session['username'], role=session['role'])

# Route for External Customers page
@app.route('/fms_external_customers')
def fms_external_customers():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_external_customers.html', username=session['username'], role=session['role'])

# Route for Invoice Management page
@app.route('/fms_invoice_management')
def fms_invoice_management():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_invoice_management.html', username=session['username'], role=session['role'])

# Route for Submitted Invoices page
@app.route('/fms_submitted_invoices')
def fms_submitted_invoices():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_submitted_invoices.html', username=session['username'], role=session['role'])

# Route for Claims Management page
@app.route('/fms_claims_management')
def fms_claims_management():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_claims_management.html', username=session['username'], role=session['role'])

# Route for Insurance Providers page
@app.route('/fms_insurance_providers')
def fms_insurance_providers():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))
    return render_template('fms_insurance_providers.html', username=session['username'], role=session['role'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('token', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
