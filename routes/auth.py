from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from config.database import db
from models.user import User

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()

def configure_login(app):
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

@auth_bp.record_once
def setup_login(state):
    configure_login(state.app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        roll = request.form["roll_no"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if User.query.filter((User.email == email) | (User.roll_no == roll)).first():
            flash("Email or roll number already exists.", "error")
            return render_template("auth/register.html")
        u = User(name=name, roll_no=roll, email=email,
                 password_hash=generate_password_hash(password), role="student")
        db.session.add(u); db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        u = User.query.filter_by(email=email).first()
        if u and check_password_hash(u.password_hash, request.form["password"]):
            login_user(u)
            return redirect(url_for("admin.dashboard") if u.role != "student" else url_for("dashboard.home"))
        flash("Invalid email or password.", "error")
    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("dashboard.home"))
