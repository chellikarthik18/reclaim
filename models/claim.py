from config.database import db

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="possible")
    reviewed_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    reviewed_at = db.Column(db.DateTime)
    email_sent_at = db.Column(db.DateTime)
    lost_item = db.relationship("Item", foreign_keys=[lost_item_id])
    found_item = db.relationship("Item", foreign_keys=[found_item_id])
