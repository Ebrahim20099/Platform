import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from dotenv import load_dotenv

from .extensions import db, login_manager
from .models import Admin, Course, ContentItem, AccessCode

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_database_uri():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url.replace("postgres://", "postgresql://", 1)
    sqlite_path = os.path.join(BASE_DIR, "instance", "app.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    return "sqlite:///" + sqlite_path


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "غيّر-السطر-ده-لأي-قيمة-سرية-قبل-النشر")
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "images")

    db.init_app(app)
    login_manager.init_app(app)

    from .admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # ---------------------- Public / student routes ----------------------

    @app.route("/")
    def index():
        courses = Course.query.filter_by(is_active=True).order_by(Course.id.desc()).all()
        return render_template("index.html", courses=[c.to_card_dict() for c in courses])

    @app.route("/api/verify-code", methods=["POST"])
    def verify_code():
        data = request.get_json(silent=True) or {}
        course_id = data.get("course_id")
        code_value = (data.get("code") or "").strip().upper()

        if not course_id or not code_value:
            return jsonify(success=False, message="من فضلك ادخل الكود"), 400

        access_code = AccessCode.query.filter_by(
            course_id=course_id, code=code_value
        ).first()

        if not access_code:
            return jsonify(success=False, message="الكود غير صحيح"), 404

        if access_code.is_used:
            return jsonify(success=False, message="الكود ده مستخدم قبل كده"), 409

        access_code.is_used = True
        from datetime import datetime
        access_code.used_at = datetime.utcnow()
        db.session.commit()

        unlocked = session.get("unlocked_courses", [])
        if course_id not in unlocked:
            unlocked.append(course_id)
        session["unlocked_courses"] = unlocked

        return jsonify(success=True, redirect_url=url_for("course_content", course_id=course_id))

    @app.route("/course/<int:course_id>/content")
    def course_content(course_id):
        course = Course.query.get_or_404(course_id)
        unlocked = session.get("unlocked_courses", [])
        if course_id not in unlocked:
            flash("لازم تشترك بالكود الأول عشان تفتح المحتوى ده", "error")
            return redirect(url_for("index"))
        return render_template("content.html", course=course)

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # اعمل أدمن افتراضي أول مرة بس (لو مفيش حد)
        if not Admin.query.first():
            default_admin = Admin(username="admin")
            default_admin.set_password("admin123")
            db.session.add(default_admin)
            db.session.commit()
            print("تم إنشاء أدمن افتراضي: admin / admin123  -- غيّر الباسورد فورًا")
    app.run(debug=True)
