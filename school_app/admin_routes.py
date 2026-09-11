import os
import csv
import io
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    current_app, send_file
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from werkzeug.utils import secure_filename

from .extensions import db
from .models import Admin, Course, ContentItem, AccessCode, EssaySubmission, ExamQuestion, StudentExamReport, StudentForumQuestion

admin_bp = Blueprint("admin", __name__, template_folder="templates")

ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp"}
ALLOWED_CONTENT_EXT = {"mp4", "webm", "ogg", "pdf"}


def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXT


def content_extension(filename):
    if "." not in filename:
        return ""
    extension = filename.rsplit(".", 1)[1].lower()
    return extension if extension in ALLOWED_CONTENT_EXT else ""


# ---------------------------- Auth ----------------------------

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for("admin.dashboard"))
        flash("يوزر أو باسورد غلط", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


# ---------------------------- Dashboard ----------------------------

@admin_bp.route("/")
@login_required
def dashboard():
    courses = Course.query.order_by(Course.id.desc()).all()
    return render_template("admin/dashboard.html", courses=courses)


@admin_bp.route("/challenges")
@login_required
def challenge_admin():
    all_users = db.session.execute(
        text("SELECT id, name, study_type, score FROM users ORDER BY score DESC, id ASC")
    ).fetchall()
    return render_template("admin/challenge_manage.html", all_users=all_users)


@admin_bp.route("/challenge/score/update", methods=["POST"])
@login_required
def challenge_score_update():
    user_id = request.form.get("user_id")
    score_delta = request.form.get("score", "0")
    reason = request.form.get("reason", "").strip()

    try:
        user_id = int(user_id)
        delta = int(score_delta)
    except (TypeError, ValueError):
        flash("القيمة غير صحيحة", "error")
        return redirect(url_for("admin.challenge_admin"))

    user = db.session.execute(
        text("SELECT id, score FROM users WHERE id = :user_id"),
        {"user_id": user_id},
    ).fetchone()
    if user is None:
        flash("الطالب غير موجود", "error")
        return redirect(url_for("admin.challenge_admin"))

    new_score = int(user["score"] or 0) + delta
    db.session.execute(
        text("UPDATE users SET score = :new_score WHERE id = :user_id"),
        {"new_score": new_score, "user_id": user_id},
    )
    if reason:
        db.session.execute(
            text("INSERT INTO challenge_scores (user_id, score, reason) VALUES (:user_id, :delta, :reason)"),
            {"user_id": user_id, "delta": delta, "reason": reason},
        )
    db.session.commit()
    flash("تم تحديث نقاط الطالب بنجاح", "success")
    return redirect(url_for("admin.challenge_admin"))


@admin_bp.route("/forum")
@login_required
def forum_admin():
    questions = StudentForumQuestion.query.order_by(StudentForumQuestion.created_at.desc()).all()
    return render_template("admin/forum_manage.html", questions=questions)


@admin_bp.route("/forum/<int:question_id>/answer", methods=["POST"])
@login_required
def forum_answer(question_id):
    question = StudentForumQuestion.query.get_or_404(question_id)
    answer = request.form.get("answer", "").strip()

    if not answer:
        flash("اكتب الإجابة أولاً", "error")
        return redirect(url_for("admin.forum_admin"))

    question.answer = answer
    question.answered_by = "admin"
    question.answered_at = datetime.utcnow()
    db.session.commit()
    flash("تم إرسال الإجابة للطلاب", "success")
    return redirect(url_for("admin.forum_admin"))


@admin_bp.route("/forum/<int:question_id>/delete", methods=["POST"])
@login_required
def forum_delete(question_id):
    question = StudentForumQuestion.query.get_or_404(question_id)
    if question.image:
        file_path = os.path.join(current_app.root_path, question.image.lstrip("/"))
        if os.path.isfile(file_path):
            os.remove(file_path)
    db.session.delete(question)
    db.session.commit()
    flash("تم حذف السؤال بنجاح", "success")
    return redirect(url_for("admin.forum_admin"))


# ---------------------------- Courses CRUD ----------------------------

@admin_bp.route("/course/new", methods=["GET", "POST"])
@login_required
def course_new():
    if request.method == "POST":
        course = Course(
            grade=request.form.get("grade"),
            grade_label=request.form.get("grade_label"),
            title=request.form.get("title"),
            date=request.form.get("date"),
            new_price=float(request.form.get("new_price") or 0),
            old_price=float(request.form["old_price"]) if request.form.get("old_price") else None,
            gradient=request.form.get("gradient") or "linear-gradient(135deg,#1f3a5f,#173a52)",
            description=request.form.get("description"),
        )

        image_file = request.files.get("image")
        if image_file and image_file.filename and allowed_image(image_file.filename):
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
            filename = secure_filename(f"course_{datetime.utcnow().timestamp()}_{image_file.filename}")
            image_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            course.image = f"/static/images/{filename}"

        db.session.add(course)
        db.session.commit()
        flash("تم إضافة الكورس بنجاح", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/course_form.html", course=None)


@admin_bp.route("/course/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
def course_edit(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == "POST":
        course.grade = request.form.get("grade")
        course.grade_label = request.form.get("grade_label")
        course.title = request.form.get("title")
        course.date = request.form.get("date")
        course.new_price = float(request.form.get("new_price") or 0)
        course.old_price = float(request.form["old_price"]) if request.form.get("old_price") else None
        course.gradient = request.form.get("gradient") or course.gradient
        course.description = request.form.get("description")
        course.is_active = bool(request.form.get("is_active"))

        image_file = request.files.get("image")
        if image_file and image_file.filename and allowed_image(image_file.filename):
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
            filename = secure_filename(f"course_{datetime.utcnow().timestamp()}_{image_file.filename}")
            image_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            course.image = f"/static/images/{filename}"

        db.session.commit()
        flash("تم تعديل الكورس", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/course_form.html", course=course)


@admin_bp.route("/course/<int:course_id>/delete", methods=["POST"])
@login_required
def course_delete(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("تم حذف الكورس وكل محتواه وأكواده", "success")
    return redirect(url_for("admin.dashboard"))


# ---------------------------- Manage content + codes ----------------------------

@admin_bp.route("/course/<int:course_id>/manage")
@login_required
def course_manage(course_id):
    course = Course.query.get_or_404(course_id)
    students = db.session.execute(
        text("""
            SELECT users.id AS user_id, users.name, users.phone, users.guardian_phone, users.email, users.grade,
                   users.study_type, course_enrollments.created_at
            FROM course_enrollments
            JOIN users ON users.id = course_enrollments.user_id
            WHERE course_enrollments.course_id = :course_id
            ORDER BY course_enrollments.created_at DESC
        """),
        {"course_id": course_id},
    ).fetchall()
    student_report_map = {
        report.user_id: report
        for report in StudentExamReport.query.filter_by(course_id=course_id).all()
    }
    essay_submissions = EssaySubmission.query.filter_by(course_id=course_id).order_by(EssaySubmission.updated_at.desc()).all()
    return render_template(
        "admin/course_manage.html",
        course=course,
        students=students,
        student_report_map=student_report_map,
        essay_submissions=essay_submissions,
    )


@admin_bp.route("/course/<int:course_id>/content/add", methods=["POST"])
@login_required
def content_add(course_id):
    course = Course.query.get_or_404(course_id)
    content_type = request.form.get("content_type", "video")
    content_file = request.files.get("content_file")
    body = request.form.get("body", "").strip()

    if content_type in {"video", "pdf"}:
        extension = content_extension(content_file.filename) if content_file else ""
        valid_type = extension == "pdf" if content_type == "pdf" else extension in {"mp4", "webm", "ogg"}
        if not content_file or not content_file.filename or not valid_type:
            flash("اختار ملفًا مطابقًا لنوع المحتوى المحدد", "error")
            return redirect(url_for("admin.course_manage", course_id=course_id))
        os.makedirs(current_app.config["CONTENT_UPLOAD_FOLDER"], exist_ok=True)
        filename = secure_filename(f"content_{datetime.utcnow().timestamp()}_{content_file.filename}")
        content_file.save(os.path.join(current_app.config["CONTENT_UPLOAD_FOLDER"], filename))
        body = f"/static/uploads/content/{filename}"

    if not body:
        flash("أدخل المحتوى أو ارفع ملفًا", "error")
        return redirect(url_for("admin.course_manage", course_id=course_id))

    item = ContentItem(
        course_id=course.id,
        title=request.form.get("title"),
        content_type=content_type,
        body=body,
        order_index=len(course.contents),
    )
    db.session.add(item)
    db.session.commit()
    flash("تمت إضافة المحتوى", "success")
    return redirect(url_for("admin.course_manage", course_id=course_id))


@admin_bp.route("/content/<int:item_id>/delete", methods=["POST"])
@login_required
def content_delete(item_id):
    item = ContentItem.query.get_or_404(item_id)
    course_id = item.course_id
    if item.body.startswith("/static/uploads/content/"):
        uploaded_path = os.path.join(current_app.root_path, item.body.lstrip("/"))
        if os.path.isfile(uploaded_path):
            os.remove(uploaded_path)
    db.session.delete(item)
    db.session.commit()
    flash("تم حذف المحتوى", "success")
    return redirect(url_for("admin.course_manage", course_id=course_id))


@admin_bp.route("/course/<int:course_id>/exam/add", methods=["POST"])
@login_required
def exam_question_add(course_id):
    course = Course.query.get_or_404(course_id)
    question_type = request.form.get("question_type", "mcq")
    if question_type not in {"mcq", "true_false", "essay"}:
        question_type = "mcq"

    try:
        marks = int(request.form.get("marks", "1").strip() or 1)
    except ValueError:
        marks = 1
    marks = max(1, marks)

    if question_type == "true_false":
        options = {"option_a": "صح", "option_b": "غلط", "option_c": "", "option_d": ""}
    elif question_type == "essay":
        options = {"option_a": "", "option_b": "", "option_c": "", "option_d": ""}
    else:
        options = {
            "option_a": request.form.get("option_a", "").strip(),
            "option_b": request.form.get("option_b", "").strip(),
            "option_c": request.form.get("option_c", "").strip(),
            "option_d": request.form.get("option_d", "").strip(),
        }

    correct_option = request.form.get("correct_option", "a").strip()
    if question_type == "essay":
        correct_option = ""
    elif question_type == "true_false" and correct_option not in {"true", "false"}:
        correct_option = "true"

    question = ExamQuestion(
        course_id=course.id,
        question=request.form.get("question", "").strip(),
        question_type=question_type,
        marks=marks,
        correct_option=correct_option,
        **options,
    )
    db.session.add(question)
    db.session.commit()
    flash("تمت إضافة سؤال الامتحان", "success")
    return redirect(url_for("admin.course_manage", course_id=course_id))


@admin_bp.route("/exam/<int:question_id>/delete", methods=["POST"])
@login_required
def exam_question_delete(question_id):
    question = ExamQuestion.query.get_or_404(question_id)
    course_id = question.course_id
    db.session.delete(question)
    db.session.commit()
    flash("تم حذف سؤال الامتحان", "success")
    return redirect(url_for("admin.course_manage", course_id=course_id))


@admin_bp.route("/course/<int:course_id>/student/<int:user_id>/report", methods=["POST"])
@login_required
def student_report_save(course_id, user_id):
    report = StudentExamReport.query.filter_by(course_id=course_id, user_id=user_id).first()
    if report is None:
        report = StudentExamReport(course_id=course_id, user_id=user_id)
        db.session.add(report)

    report.achievements = request.form.get("achievements", "").strip()
    report.weak_points = request.form.get("weak_points", "").strip()
    report.admin_analysis = request.form.get("admin_analysis", "").strip()
    db.session.commit()
    flash("تم حفظ تقرير الطالب بنجاح", "success")
    return redirect(url_for("admin.course_manage", course_id=course_id))


@admin_bp.route("/essay/<int:submission_id>/grade", methods=["POST"])
@login_required
def essay_grade_save(submission_id):
    submission = EssaySubmission.query.get_or_404(submission_id)
    try:
        score = int(request.form.get("score", "0").strip() or 0)
    except ValueError:
        score = 0

    submission.score = max(0, min(score, submission.question.marks if submission.question else score))
    submission.feedback = request.form.get("feedback", "").strip()
    submission.status = "graded"
    db.session.commit()

    report = StudentExamReport.query.filter_by(course_id=submission.course_id, user_id=submission.user_id).first()
    if report is not None:
        course = Course.query.get(submission.course_id)
        all_essay_questions = [question for question in course.exam_questions if question.question_type == "essay"]
        essay_question_ids = {question.id for question in all_essay_questions}
        student_essay_submissions = EssaySubmission.query.filter_by(
            course_id=submission.course_id,
            user_id=submission.user_id,
        ).all()
        graded_question_ids = {item.question_id for item in student_essay_submissions if item.status == "graded"}

        objective_total = sum(question.marks for question in course.exam_questions if question.question_type != "essay")
        essay_total = sum(question.marks for question in all_essay_questions)
        prior_essay_score = sum(
            item.score for item in student_essay_submissions
            if item.status == "graded" and item.id != submission.id
        )
        objective_score = max(0, (report.score or 0) - prior_essay_score)
        essay_score = sum(item.score for item in student_essay_submissions if item.status == "graded")

        if not all_essay_questions or essay_question_ids.issubset(graded_question_ids):
            report.score = objective_score + essay_score
            report.total = objective_total + essay_total
            report.result_status = "ready"
            report.review_summary = "تم التصحيح"
        else:
            report.score = objective_score
            report.total = objective_total
            report.result_status = "pending"
            report.review_summary = "قيد التصحيح"
        db.session.commit()

    flash("تم تصحيح السؤال المقالي", "success")
    return redirect(url_for("admin.course_manage", course_id=submission.course_id))


# ---------------------------- Access codes ----------------------------

@admin_bp.route("/course/<int:course_id>/codes/generate", methods=["POST"])
@login_required
def codes_generate(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        count = int(request.form.get("count", 30))
    except ValueError:
        count = 30
    count = max(1, min(count, 500))

    for _ in range(count):
        code = AccessCode.generate_unique_code()
        db.session.add(AccessCode(course_id=course.id, code=code))
    db.session.commit()

    flash(f"تم توليد {count} كود جديد للكورس ده", "success")
    return redirect(url_for("admin.course_manage", course_id=course_id))


@admin_bp.route("/code/<int:code_id>/delete", methods=["POST"])
@login_required
def code_delete(code_id):
    code = AccessCode.query.get_or_404(code_id)
    course_id = code.course_id
    db.session.delete(code)
    db.session.commit()
    return redirect(url_for("admin.course_manage", course_id=course_id))


@admin_bp.route("/course/<int:course_id>/codes/export")
@login_required
def codes_export(course_id):
    course = Course.query.get_or_404(course_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["code", "is_used", "used_at"])
    for c in course.codes:
        writer.writerow([c.code, "used" if c.is_used else "available", c.used_at or ""])

    mem = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    filename = f"codes_course_{course_id}.csv"
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name=filename)
