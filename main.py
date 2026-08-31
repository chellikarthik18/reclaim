import os, socket
from flask import Flask
from config.database import db, init_db
from routes.auth import auth_bp
from routes.lost import lost_bp
from routes.found import found_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "reclaim-dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campus_lost_found.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024

db.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(lost_bp)
app.register_blueprint(found_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)

@app.route("/uploads/<path:filename>")
def static_upload(filename):
    from flask import send_from_directory
    return send_from_directory(os.path.join(app.root_path, "uploads"), filename)

@app.context_processor
def inject_globals():
    return {"app_name": "RECLAIM", "tagline": "Lost it. Found it. Reclaim it."}

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "YOUR-LAN-IP"

if __name__ == "__main__":
    with app.app_context():
        init_db()
    print("\nRECLAIM is running.")
    print("Local:   http://127.0.0.1:5000")
    print(f"Network: http://{local_ip()}:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
