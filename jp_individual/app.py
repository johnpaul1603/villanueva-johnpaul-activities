from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecret'

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="jp"
    )

# Routes
@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)", (fullname, email, password))
        conn.commit()
        conn.close()

        flash('Signup successful. Please login.')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password_input):
            session['user_id'] = user['id']
            session['fullname'] = user['fullname']
            return redirect('/dashboard')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        salary = request.form['salary']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)", (name, position, salary))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        salary = request.form['salary']
        cursor.execute("UPDATE employees SET name=%s, position=%s, salary=%s WHERE id=%s", (name, position, salary, id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()
    conn.close()
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
