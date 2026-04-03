from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import csrf
from app.config import get_db_connection

csrf_bp = Blueprint("csrf_demo", __name__)


@csrf_bp.route("/vulnerable", methods=["GET"])
@login_required
def vulnerable():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT balance FROM users WHERE id = %s", (current_user.id,))
            user_data = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM transfers WHERE from_user_id = %s ORDER BY created_at DESC",
                (current_user.id,),
            )
            transfers = cursor.fetchall()
    finally:
        conn.close()

    return render_template(
        "csrf/vulnerable.html",
        balance=user_data["balance"],
        transfers=transfers,
    )


@csrf_bp.route("/vulnerable/transfer", methods=["POST"])
@login_required
@csrf.exempt  # Intentionally vulnerable: no CSRF protection
def vulnerable_transfer():
    to_username = request.form.get("to_username", "").strip()
    amount = request.form.get("amount", "0")

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        flash("Số tiền không hợp lệ.", "error")
        return redirect(url_for("csrf_demo.vulnerable"))

    if amount <= 0:
        flash("Số tiền phải lớn hơn 0.", "error")
        return redirect(url_for("csrf_demo.vulnerable"))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check balance
            cursor.execute("SELECT balance FROM users WHERE id = %s", (current_user.id,))
            user = cursor.fetchone()

            if user["balance"] < amount:
                flash("Số dư không đủ!", "error")
                return redirect(url_for("csrf_demo.vulnerable"))

            # Check recipient exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (to_username,))
            recipient = cursor.fetchone()
            if not recipient:
                flash("Người nhận không tồn tại.", "error")
                return redirect(url_for("csrf_demo.vulnerable"))

            # VULNERABLE: No CSRF token verification
            cursor.execute(
                "UPDATE users SET balance = balance - %s WHERE id = %s",
                (amount, current_user.id),
            )
            cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE username = %s",
                (amount, to_username),
            )
            cursor.execute(
                "INSERT INTO transfers (from_user_id, to_username, amount) VALUES (%s, %s, %s)",
                (current_user.id, to_username, amount),
            )

            flash(f"Đã chuyển ${amount:.2f} cho {to_username}! (KHÔNG CÓ CSRF PROTECTION)", "warning")
    finally:
        conn.close()

    return redirect(url_for("csrf_demo.vulnerable"))


@csrf_bp.route("/secure", methods=["GET"])
@login_required
def secure():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT balance FROM users WHERE id = %s", (current_user.id,))
            user_data = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM transfers WHERE from_user_id = %s ORDER BY created_at DESC",
                (current_user.id,),
            )
            transfers = cursor.fetchall()
    finally:
        conn.close()

    return render_template(
        "csrf/secure.html",
        balance=user_data["balance"],
        transfers=transfers,
    )


@csrf_bp.route("/secure/transfer", methods=["POST"])
@login_required
# CSRF token is automatically validated by Flask-WTF
def secure_transfer():
    to_username = request.form.get("to_username", "").strip()
    amount = request.form.get("amount", "0")

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        flash("Số tiền không hợp lệ.", "error")
        return redirect(url_for("csrf_demo.secure"))

    if amount <= 0:
        flash("Số tiền phải lớn hơn 0.", "error")
        return redirect(url_for("csrf_demo.secure"))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT balance FROM users WHERE id = %s", (current_user.id,))
            user = cursor.fetchone()

            if user["balance"] < amount:
                flash("Số dư không đủ!", "error")
                return redirect(url_for("csrf_demo.secure"))

            cursor.execute("SELECT id FROM users WHERE username = %s", (to_username,))
            recipient = cursor.fetchone()
            if not recipient:
                flash("Người nhận không tồn tại.", "error")
                return redirect(url_for("csrf_demo.secure"))

            cursor.execute(
                "UPDATE users SET balance = balance - %s WHERE id = %s",
                (amount, current_user.id),
            )
            cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE username = %s",
                (amount, to_username),
            )
            cursor.execute(
                "INSERT INTO transfers (from_user_id, to_username, amount) VALUES (%s, %s, %s)",
                (current_user.id, to_username, amount),
            )

            flash(f"Đã chuyển ${amount:.2f} cho {to_username}! (CÓ CSRF PROTECTION ✓)", "success")
    finally:
        conn.close()

    return redirect(url_for("csrf_demo.secure"))
