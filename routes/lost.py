import os, uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from config.database import db
from models.item import Item
from models.notification import Notification

lost_bp = Blueprint("lost", __name__)
ALLOWED = {"jpg", "jpeg", "png", "webp"}

def save_image(file, folder):
    if not file or not file.filename: return None
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED: raise ValueError("Only JPG, JPEG, PNG and WEBP images are allowed.")
    name = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    path = os.path.join(current_app.root_path, "uploads", folder)
    os.makedirs(path, exist_ok=True)
    file.save(os.path.join(path, name))
    return f"{folder}/{name}"

@lost_bp.route("/lost", methods=["GET", "POST"])
@login_required
def report_lost():
    if request.method == "POST":
        try:
            item = Item(
                type="lost", reported_by=current_user.id,
                category=request.form["category"], brand=request.form.get("brand"),
                model=request.form.get("model"), color=request.form.get("color"),
                details=request.form.get("details"), location=request.form["location"],
                date=request.form["date"], time=request.form.get("time")
            )
            item.image_path = save_image(request.files.get("image"), "lost")
            db.session.add(item)
            db.session.flush()
            db.session.add(Notification(user_id=current_user.id, title="Lost report submitted",
                message="RECLAIM will continue searching until a matching found item is registered.", type="success"))
            db.session.commit()
            flash("Lost item report submitted successfully.", "success")
            return redirect(url_for("dashboard.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("student/lost_item.html")
