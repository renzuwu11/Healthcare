from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patient_management')
def patient_management():
    return render_template('patient_management.html')  # Placeholder for patient management page

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')  

@app.route('/login')
def login():
    return render_template('login.html')  

@app.route('/login', methods=['POST'])
def login_post():
    return render_template('admin_dashboard.html')

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

