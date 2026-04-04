from flask import Blueprint, render_template
from app.config import get_db_connection

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    conn = get_db_connection()
    demo_users = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username, balance, role FROM users LIMIT 5")
            demo_users = cursor.fetchall()
            # Map password for display (hardcoded for demo simplicity since we use seed passwords)
            passwords = {
                "admin": "admin123",
                "alice": "alice123",
                "bob": "bob123",
                "charlie": "charlie123",
                "attacker": "hack3r"
            }
            for user in demo_users:
                user['password'] = passwords.get(user['username'], "******")
    finally:
        conn.close()
    attacks = [
        {
            "name": "SQL Injection",
            "icon": "database-zap.svg",
            "severity": "Critical",
            "description": "Chèn mã SQL độc hại vào input để truy cập, sửa đổi hoặc xóa dữ liệu trong database.",
            "url": "/sqli/vulnerable",
            "color": "#ff4757",
        },
        {
            "name": "Cross-Site Scripting (XSS)",
            "icon": "terminal.svg",
            "severity": "High",
            "description": "Chèn JavaScript độc vào trang web để đánh cắp cookie, session hoặc thực thi hành động thay user.",
            "url": "/xss/vulnerable",
            "color": "#ff6348",
        },
        {
            "name": "Cross-Site Request Forgery",
            "icon": "send.svg",
            "severity": "High",
            "description": "Lừa user đã đăng nhập thực hiện hành động không mong muốn trên web app mà họ đang trust.",
            "url": "/csrf/vulnerable",
            "color": "#ffa502",
        },
        {
            "name": "File Upload & IDOR",
            "icon": "fingerprint-pattern.svg",
            "severity": "High",
            "description": "Upload file độc hại hoặc truy cập tài nguyên của user khác bằng cách thay đổi ID trong URL.",
            "url": "/upload/vulnerable",
            "color": "#ff4757",
        },
    ]
    return render_template("index.html", attacks=attacks, demo_users=demo_users)
