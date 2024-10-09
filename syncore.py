from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/patient_management')
def patient_management():
    return render_template('patient_management.html')  # Placeholder for patient management page

@app.route('/admin_control')
def admin_control():
    return render_template('admin_control.html')  # Placeholder for patient management page


if __name__ == '__main__':
    app.run(debug=True)
