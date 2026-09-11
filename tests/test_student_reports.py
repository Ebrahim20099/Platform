import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from school_app.extensions import db
from school_app.models import Course, ExamQuestion, StudentExamReport


def test_student_report_is_saved_with_weak_points():
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        course = Course(
            grade='first',
            grade_label='الصف الأول الثانوي',
            title='Test Course',
            new_price=0,
            description='desc',
        )
        db.session.add(course)
        db.session.commit()

        q1 = ExamQuestion(
            course_id=course.id,
            question='Q1',
            question_type='mcq',
            option_a='1',
            option_b='2',
            correct_option='a',
            marks=5,
        )
        q2 = ExamQuestion(
            course_id=course.id,
            question='Q2',
            question_type='mcq',
            option_a='x',
            option_b='y',
            correct_option='b',
            marks=3,
        )
        db.session.add_all([q1, q2])
        db.session.commit()

        report = StudentExamReport(
            user_id=10,
            course_id=course.id,
            score=5,
            total=8,
            achievements='مستوى جيد',
            weak_points='Q1',
            admin_analysis='راجع الأساسيات',
        )
        db.session.add(report)
        db.session.commit()

        saved = StudentExamReport.query.filter_by(user_id=10, course_id=course.id).first()
        assert saved is not None
        assert saved.score == 5
        assert saved.total == 8
        assert 'Q1' in saved.weak_points
