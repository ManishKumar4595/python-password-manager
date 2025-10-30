from flask import Flask, render_template, request, redirect, url_for, flash, session
import os, random, string
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mysecretkey'

users = {}  # Store users in memory (use DB in real world)

@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return render_template('index.html', user=user)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            session['user'] = users[email]
            flash(f"Welcome back, {users[email]['name']}!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password!", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if email in users:
            flash("Email already registered!", "warning")
        else:
            user_id = len(users) + 1
            users[email] = {
                "id": user_id,
                "name": name,
                "email": email,
                "password": password,
                "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        if email in users:
            new_pass = ''.join(random.choices(string.digits, k=4))
            users[email]['password'] = new_pass
            flash(f"Your new password is: {new_pass}", "info")
        else:
            flash("Email not found!", "danger")
    return render_template('forgot.html')

if __name__ == '__main__':
    app.run(debug=True)

