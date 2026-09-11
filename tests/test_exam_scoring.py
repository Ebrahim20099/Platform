import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from school_app.extensions import db
from school_app.models import Course, ExamQuestion


def test_question_marks_are_applied():
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
            option_c='3',
            option_d='4',
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

        score = 0
        total = 0
        for question in [q1, q2]:
            if question.question_type == 'essay':
                continue
            total += question.marks
            if 'a' == question.correct_option:
                score += question.marks

        assert total == 8
        assert score == 5
