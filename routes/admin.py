from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from config.database import db
from models.item import Item
from models.claim import Claim
from models.notification import Notification
from services.email_service import send_found_item_email

admin_bp = Blueprint("admin", __name__, url_prefix="/helpline")

def staff_required():
    return current_user.is_authenticated and current_user.role in ("helpline_staff", "admin")

@admin_bp.before_request
def protect():
    if not staff_required():
        return redirect(url_for("auth.login"))

@admin_bp.route("/")
@login_required
def dashboard():
    return render_template("admin/dashboard.html",
        active=Item.query.filter_by(type="lost", status="searching").count(),
        found=Item.query.filter_by(type="found").count(),
        possible=Claim.query.filter_by(status="possible").count(),
        reclaimed=Item.query.filter_by(status="closed").count())

@admin_bp.route("/matches")
@login_required
def matches():
    claims = Claim.query.order_by(Claim.id.desc()).all()
    return render_template("admin/matches.html", claims=claims)

@admin_bp.route("/matches/<int:claim_id>/reject", methods=["POST"])
@login_required
def reject(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    claim.status = "rejected"
    claim.reviewed_by = current_user.id
    claim.reviewed_at = datetime.utcnow()
    claim.lost_item.status = "searching"
    db.session.commit()
    flash("Match rejected. Lost case remains active.", "success")
    return redirect(url_for("admin.matches"))

@admin_bp.route("/matches/<int:claim_id>/send-email", methods=["POST"])
@login_required
def send_email(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    if claim.status not in ("possible", "verified"):
        flash("This match is not eligible for notification.", "error")
        return redirect(url_for("admin.matches"))

    # Explicit human action: email is sent ONLY from this button.
    try:
        student = claim.lost_item.reporter
        send_found_item_email(student.email, student.name, claim.found_item)
        claim.status = "notified"
        claim.email_sent_at = datetime.utcnow()
        claim.reviewed_by = current_user.id
        claim.reviewed_at = datetime.utcnow()
        claim.lost_item.status = "closed"
        db.session.add(Notification(user_id=student.id, title="Item verified and email sent",
            message="The Helpline Centre verified your item and sent you an email with collection instructions.", type="success"))
        db.session.commit()
        flash(f"Email sent successfully to {student.email}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Email failed: {e}", "error")
    return redirect(url_for("admin.matches"))

@admin_bp.route("/matches/<int:claim_id>/verify", methods=["POST"])
@login_required
def verify(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    claim.status = "verified"
    claim.reviewed_by = current_user.id
    claim.reviewed_at = datetime.utcnow()
    db.session.commit()
    flash("Match verified by Helpline Centre. Email has NOT been sent automatically.", "success")
    return redirect(url_for("admin.matches"))
