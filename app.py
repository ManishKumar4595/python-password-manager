from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- DATABASE SETUP ----------
DB_FILE = "passwords.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)
        cur.execute("""
        CREATE TABLE passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            website TEXT,
            username TEXT,
            password TEXT
        )
        """)
        conn.commit()
        conn.close()

init_db()

# ---------- ROUTES ----------

@app.route('/')
def home():
    return render_template('login.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()
    conn.close()

    if user:
        session['email'] = email
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password!", "error")
        return redirect(url_for('home'))

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            flash("Registration successful! You can now login.", "success")
        except sqlite3.IntegrityError:
            flash("Email already exists!", "error")
        conn.close()
        return redirect(url_for('home'))
    return render_template('register.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('home'))

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM passwords WHERE user_email=?", (session['email'],))
    data = cur.fetchall()
    conn.close()

    # convert tuples into dicts for Jinja2 readability
    data = [{'id': d[0], 'website': d[2], 'username': d[3], 'password': d[4]} for d in data]
    return render_template('index.html', data=data)

# ---------- SAVE PASSWORD ----------
@app.route('/save', methods=['POST'])
def save_password():
    if 'email' not in session:
        return redirect(url_for('home'))

    website = request.form['website']
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO passwords (user_email, website, username, password) VALUES (?, ?, ?, ?)",
                (session['email'], website, username, password))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# ---------- UPDATE PASSWORD ----------
@app.route('/update', methods=['POST'])
def update_password():
    if 'email' not in session:
        return redirect(url_for('home'))

    website = request.form['website']
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        UPDATE passwords
        SET username=?, password=?
        WHERE user_email=? AND website=?
    """, (username, password, session['email'], website))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# ---------- DELETE PASSWORD ----------
@app.route('/delete', methods=['POST'])
def delete_password():
    if 'email' not in session:
        return redirect(url_for('home'))

    website = request.form['website']

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM passwords WHERE user_email=? AND website=?", (session['email'], website))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# ---------- SEARCH PASSWORD ----------
@app.route('/search')
def search_password():
    if 'email' not in session:
        return redirect(url_for('home'))

    query = request.args.get('query', '')

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM passwords
        WHERE user_email=? AND website LIKE ?
    """, (session['email'], f'%{query}%'))
    data = cur.fetchall()
    conn.close()

    data = [{'id': d[0], 'website': d[2], 'username': d[3], 'password': d[4]} for d in data]
    return render_template('index.html', data=data)

# ---------- LOGOUT ----------
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

# ---------- RUN APP ----------
if __name__ == '__main__':
    app.run(debug=True)
