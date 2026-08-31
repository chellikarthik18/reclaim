from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


def init_db():
    # Import models only after db has been created.
    from models.user import User
    from models.item import Item
    from models.claim import Claim
    from models.notification import Notification

    db.create_all()

    # Create demo Helpline account
    if not User.query.filter_by(email="admin@reclaim.local").first():
        admin = User(
            roll_no="ADMIN001",
            name="Helpline Administrator",
            email="admin@reclaim.local",
            password_hash=generate_password_hash("admin123"),
            role="helpline_staff"
        )

        db.session.add(admin)
        db.session.commit()

        print("Demo Helpline login:")
        print("Email: admin@reclaim.local")
        print("Password: admin123")