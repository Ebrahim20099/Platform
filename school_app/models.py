import random
import string
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Course(db.Model):
    """كورس / باقة زي اللي كانت في الداتا الثابتة الأول"""
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(20), nullable=False)          # first / second / third
    grade_label = db.Column(db.String(100), nullable=False)   # الصف الأول الثانوي
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50), default="")
    new_price = db.Column(db.Float, nullable=False, default=0)
    old_price = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(255), nullable=True)          # مسار صورة مرفوعة
    gradient = db.Column(db.String(255), default="linear-gradient(135deg,#1f3a5f,#173a52)")
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contents = db.relationship(
        "ContentItem", backref="course", cascade="all, delete-orphan",
        order_by="ContentItem.order_index"
    )
    codes = db.relationship("AccessCode", backref="course", cascade="all, delete-orphan")

    def unused_codes_count(self):
        return sum(1 for c in self.codes if not c.is_used)

    def to_card_dict(self):
        return {
            "id": self.id,
            "grade": self.grade,
            "gradeLabel": self.grade_label,
            "title": self.title,
            "date": self.date,
            "newPrice": self.new_price,
            "oldPrice": self.old_price,
            "image": self.image,
            "gradient": self.gradient,
        }


class ContentItem(db.Model):
    """عنصر محتوى تعليمي جوه الكورس (فيديو / ملف / رابط / نص)"""
    __tablename__ = "content_items"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(20), nullable=False, default="video")  # video/pdf/link/text
    body = db.Column(db.Text, nullable=False)  # رابط الفيديو / رابط الملف / النص
    order_index = db.Column(db.Integer, default=0)


class AccessCode(db.Model):
    """كود اشتراك بيفتح محتوى الكورس ده"""
    __tablename__ = "access_codes"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    student_note = db.Column(db.String(255), nullable=True)  # اسم/رقم الطالب لو حبيت تسجله
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_unique_code(length=8):
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choices(alphabet, k=length))
            if not AccessCode.query.filter_by(code=code).first():
                return code


class CourseEnrollment(db.Model):
    __tablename__ = "course_enrollments"
    __table_args__ = (db.UniqueConstraint("user_id", "course_id", name="uq_user_course"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    course = db.relationship("Course", backref=db.backref("enrollments", cascade="all, delete-orphan"))


class ChallengeScore(db.Model):
    __tablename__ = "challenge_scores"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False, default=0)
    reason = db.Column(db.String(255), nullable=True, default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class StudentForumQuestion(db.Model):
    __tablename__ = "student_forum_questions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True, default="")
    answer = db.Column(db.Text, nullable=True, default="")
    answered_by = db.Column(db.String(100), nullable=True, default="")
    answered_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def status(self):
        return "answered" if self.answer else "open"


class EssaySubmission(db.Model):
    __tablename__ = "essay_submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("exam_questions.id"), nullable=False, index=True)
    answer = db.Column(db.Text, nullable=True, default="")
    score = db.Column(db.Integer, nullable=False, default=0)
    feedback = db.Column(db.Text, nullable=True, default="")
    status = db.Column(db.String(30), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    course = db.relationship("Course", backref=db.backref("essay_submissions", cascade="all, delete-orphan"))
    question = db.relationship("ExamQuestion", backref=db.backref("essay_submissions", cascade="all, delete-orphan"))


class StudentExamReport(db.Model):
    __tablename__ = "student_exam_reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False, default=0)
    total = db.Column(db.Integer, nullable=False, default=0)
    result_status = db.Column(db.String(30), nullable=False, default="pending")
    review_summary = db.Column(db.Text, nullable=True, default="")
    achievements = db.Column(db.Text, nullable=True, default="")
    weak_points = db.Column(db.Text, nullable=True, default="")
    admin_analysis = db.Column(db.Text, nullable=True, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    course = db.relationship("Course", backref=db.backref("student_reports", cascade="all, delete-orphan"))

    @property
    def percentage(self):
        if self.total <= 0:
            return 0
        return round((self.score / self.total) * 100, 2)


class ExamQuestion(db.Model):
    __tablename__ = "exam_questions"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False, default="mcq")  # mcq / true_false / essay
    marks = db.Column(db.Integer, nullable=False, default=1)
    option_a = db.Column(db.String(255), nullable=True)
    option_b = db.Column(db.String(255), nullable=True)
    option_c = db.Column(db.String(255), nullable=True)
    option_d = db.Column(db.String(255), nullable=True)
    correct_option = db.Column(db.String(255), nullable=True)
    course = db.relationship("Course", backref=db.backref("exam_questions", cascade="all, delete-orphan", order_by="ExamQuestion.id"))
