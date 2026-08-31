from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.item import Item
from models.notification import Notification

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def home():
    return render_template("index.html")

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    lost = Item.query.filter_by(reported_by=current_user.id, type="lost").order_by(Item.id.desc()).all()
    found = Item.query.filter_by(reported_by=current_user.id, type="found").order_by(Item.id.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.id.desc()).all()
    return render_template("student/dashboard.html", lost=lost, found=found, notifications=notifications)
