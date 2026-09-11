import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from school_app.extensions import db
from school_app.models import Course, ExamQuestion, EssaySubmission, StudentExamReport


def test_manual_grading_keeps_result_hidden_until_all_essay_questions_are_graded():
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        course = Course(
            grade='first',
            grade_label='الصف الأول الثانوي',
            title='Manual Grading Course',
            new_price=0,
            description='desc',
        )
        db.session.add(course)
        db.session.commit()

        question = ExamQuestion(
            course_id=course.id,
            question='سؤال مقالي',
            question_type='essay',
            marks=10,
        )
        db.session.add(question)
        db.session.commit()

        report = StudentExamReport(
            user_id=1,
            course_id=course.id,
            score=0,
            total=0,
            result_status='pending',
            review_summary='قيد التصحيح',
        )
        db.session.add(report)
        db.session.commit()

        submission = EssaySubmission(
            user_id=1,
            course_id=course.id,
            question_id=question.id,
            answer='إجابة الطالب',
            status='pending',
            score=0,
        )
        db.session.add(submission)
        db.session.commit()

        assert report.result_status == 'pending'
        assert report.score == 0
        assert report.total == 0
        assert 'قيد التصحيح' in report.review_summary
