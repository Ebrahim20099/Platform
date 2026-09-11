import os
import sqlite3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, get_db, get_challenge_leaders


def test_challenge_leaders_are_split_by_study_type():
    with app.app_context():
        database = get_db()
        database.execute("DELETE FROM users")
        database.execute(
            "INSERT INTO users (name, phone, email, grade, study_type, password, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("A", "111", "a@test.com", "first", "center", "x", 90),
        )
        database.execute(
            "INSERT INTO users (name, phone, email, grade, study_type, password, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("B", "222", "b@test.com", "first", "center", "x", 50),
        )
        database.execute(
            "INSERT INTO users (name, phone, email, grade, study_type, password, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("C", "333", "c@test.com", "first", "center", "x", 40),
        )
        database.execute(
            "INSERT INTO users (name, phone, email, grade, study_type, password, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("D", "444", "d@test.com", "first", "online", "x", 100),
        )
        database.execute(
            "INSERT INTO users (name, phone, email, grade, study_type, password, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("E", "555", "e@test.com", "first", "online", "x", 80),
        )
        database.commit()

        leaders = get_challenge_leaders()
        assert [student["name"] for student in leaders["center"]] == ["A", "B", "C"]
        assert [student["name"] for student in leaders["online"]] == ["D", "E"]
