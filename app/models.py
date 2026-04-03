from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import get_db_connection


class User(UserMixin):
    def __init__(self, id, username, password_hash, email, role, balance=1000.0):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role
        self.balance = balance

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cursor.fetchone()
                if row:
                    return User(**row)
                return None
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                row = cursor.fetchone()
                if row:
                    return User(**row)
                return None
        finally:
            conn.close()

    @staticmethod
    def create(username, password, email, role="user"):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)",
                    (username, password_hash, email, role),
                )
                return cursor.lastrowid
        finally:
            conn.close()
