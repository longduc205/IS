from flask import Blueprint, render_template, request
from app.config import get_db_connection

sqli_bp = Blueprint("sqli", __name__)

PAYLOADS = [
    {"name": "Basic Auth Bypass", "value": "' OR '1'='1", "description": "Trả về tất cả users vì điều kiện luôn đúng"},
    {"name": "UNION Data Extract", "value": "' UNION SELECT id, username, email, role, balance FROM users-- ", "description": "Lấy toàn bộ thông tin users bằng UNION (5 cột)"},
    {"name": "Comment Bypass", "value": "admin'-- ", "description": "Bỏ qua phần còn lại của query bằng comment"},
    {"name": "Always True", "value": "' OR 1=1-- ", "description": "Điều kiện luôn TRUE, bypass filter"},
]


@sqli_bp.route("/vulnerable", methods=["GET"])
def vulnerable():
    search = request.args.get("search", "")
    results = []
    executed_query = ""
    error_msg = ""

    if search:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # VULNERABLE: String concatenation — DO NOT use in production
                query = f"SELECT id, username, email, role, balance FROM users WHERE username = '{search}'"
                executed_query = query
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                except Exception as e:
                    error_msg = str(e)
        finally:
            conn.close()

    return render_template(
        "sqli/vulnerable.html",
        search=search,
        results=results,
        executed_query=executed_query,
        error_msg=error_msg,
        payloads=PAYLOADS,
    )


@sqli_bp.route("/secure", methods=["GET"])
def secure():
    search = request.args.get("search", "")
    results = []
    executed_query = ""

    if search:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # SECURE: Parameterized query
                query = "SELECT id, username, email, role FROM users WHERE username = %s"
                executed_query = f"SELECT id, username, email, role FROM users WHERE username = '{conn.escape_string(search)}'"
                cursor.execute(query, (search,))
                results = cursor.fetchall()
        finally:
            conn.close()

    return render_template(
        "sqli/secure.html",
        search=search,
        results=results,
        executed_query=executed_query,
        payloads=PAYLOADS,
    )
