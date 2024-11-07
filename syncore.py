from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
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
