from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, random, string
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ---- Database setup ----
def init_db():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS passwords(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    website TEXT,
                    username TEXT,
                    password TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )''')
    conn.commit()
    conn.close()

init_db()

# ---- Routes ----

@app.route('/')
def home():
    return redirect(url_for('login'))

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except:
            flash("Email already exists!", "error")
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['email'] = email
            flash(f"Welcome back, {email}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid login details!", "error")
    return render_template('login.html')

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('login'))

    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM passwords WHERE user_id=?", (session['user_id'],))
    total = c.fetchone()[0]
    conn.close()

    return render_template('dashboard.html', user=session['email'], total=total)

# Save new password
@app.route('/save', methods=['POST'])
def save():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    website = request.form['website']
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("INSERT INTO passwords (user_id, website, username, password) VALUES (?, ?, ?, ?)",
              (session['user_id'], website, username, password))
    conn.commit()
    conn.close()

    flash("Password saved successfully!", "success")
    return redirect(url_for('dashboard'))

# Show all passwords
@app.route('/showall')
def showall():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("SELECT id, website, username, password FROM passwords WHERE user_id=?", (session['user_id'],))
    data = c.fetchall()
    conn.close()

    return render_template('dashboard.html', user=session['email'], data=data, total=len(data))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
