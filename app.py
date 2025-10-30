from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ---------------------------------------------------
# 1. App Configuration
# ---------------------------------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"  # change if deploying publicly
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///password_manager.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------------------------------
# 2. Database Models
# ---------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    passwords = db.relationship("Password", backref="user", lazy=True)


class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# ---------------------------------------------------
# 3. Routes
# ---------------------------------------------------

# Home → Login Page
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("login.html")


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if email exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.", "error")
            return redirect("/")

        # Save new user
        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect("/")

    return render_template("register.html")


# Login
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["user_email"] = user.email
        return redirect("/dashboard")
    else:
        flash("Invalid email or password!", "error")
        return redirect("/")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/")


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    passwords = Password.query.filter_by(user_id=session["user_id"]).all()
    return render_template("dashboard.html", passwords=passwords)


# Add new password
@app.route("/add", methods=["POST"])
def add_password():
    if "user_id" not in session:
        return redirect("/")

    site = request.form["site"]
    username = request.form["username"]
    password = request.form["password"]

    new_entry = Password(site=site, username=username, password=password, user_id=session["user_id"])
    db.session.add(new_entry)
    db.session.commit()

    flash("Password added successfully!", "success")
    return redirect("/dashboard")


# Delete password
@app.route("/delete/<int:id>")
def delete_password(id):
    if "user_id" not in session:
        return redirect("/")

    entry = Password.query.get_or_404(id)
    if entry.user_id != session["user_id"]:
        flash("Unauthorized action!", "error")
        return redirect("/dashboard")

    db.session.delete(entry)
    db.session.commit()
    flash("Password deleted successfully!", "info")
    return redirect("/dashboard")


# Edit/Update password
@app.route("/edit/<int:id>", methods=["POST"])
def edit_password(id):
    if "user_id" not in session:
        return redirect("/")

    entry = Password.query.get_or_404(id)
    if entry.user_id != session["user_id"]:
        flash("Unauthorized action!", "error")
        return redirect("/dashboard")

    entry.site = request.form["site"]
    entry.username = request.form["username"]
    entry.password = request.form["password"]
    db.session.commit()
    flash("Password updated successfully!", "success")
    return redirect("/dashboard")


# ---------------------------------------------------
# 4. Create Database Tables
# ---------------------------------------------------
if not os.path.exists("password_manager.db"):
    with app.app_context():
        db.create_all()


# ---------------------------------------------------
# 5. Run App
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
