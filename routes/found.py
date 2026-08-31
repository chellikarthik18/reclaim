import os, uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from config.database import db
from models.item import Item
from models.claim import Claim
from models.notification import Notification
from services.matching import generate_possible_matches

found_bp = Blueprint("found", __name__)
ALLOWED = {"jpg", "jpeg", "png", "webp"}

def save_image(file):
    if not file or not file.filename: return None
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED: raise ValueError("Only JPG, JPEG, PNG and WEBP images are allowed.")
    name = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    path = os.path.join(current_app.root_path, "uploads", "found")
    os.makedirs(path, exist_ok=True)
    file.save(os.path.join(path, name))
    return f"found/{name}"

@found_bp.route("/found", methods=["GET", "POST"])
@login_required
def report_found():
    if request.method == "POST":
        try:
            item = Item(
                type="found", reported_by=current_user.id,
                category=request.form["category"], brand=request.form.get("brand"),
                model=request.form.get("model"), color=request.form.get("color"),
                details=request.form.get("details"), location=request.form["location"],
                date=request.form["date"], time=request.form.get("time"),
                image_path=save_image(request.files.get("image")), status="registered"
            )
            db.session.add(item); db.session.flush()
            db.session.add(Notification(user_id=current_user.id, title="Found item registered",
                message="Please keep the physical item safely with the Student Helpline Centre.", type="success"))

            # AI/software-assisted only: create POSSIBLE matches; never verify or email automatically.
            for lost, score in generate_possible_matches(item):
                if not Claim.query.filter_by(lost_item_id=lost.id, found_item_id=item.id).first():
                    db.session.add(Claim(lost_item_id=lost.id, found_item_id=item.id, match_score=score, status="possible"))
                    lost.status = "possible_match"
                    db.session.add(Notification(user_id=lost.reported_by, title="Possible match found",
                        message="The Helpline Centre is reviewing a possible match. No ownership decision has been made.", type="info"))
            db.session.commit()
            flash("Found item registered. Possible matches have been sent to the Helpline Centre for human review.", "success")
            return redirect(url_for("dashboard.dashboard"))
        except Exception as e:
            db.session.rollback(); flash(str(e), "error")
    return render_template("student/found_item.html")
