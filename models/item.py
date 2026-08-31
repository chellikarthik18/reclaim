from config.database import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)  # lost/found
    category = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(120))
    model = db.Column(db.String(120))
    color = db.Column(db.String(80))
    details = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20))
    image_path = db.Column(db.String(500))
    reported_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(30), default="searching")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    reporter = db.relationship("User", foreign_keys=[reported_by])
