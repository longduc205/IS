import os
import uuid
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, abort
from flask_login import login_required, current_user
from app import csrf
from app.config import get_db_connection
from flask import current_app

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/vulnerable", methods=["GET", "POST"])
@csrf.exempt
def vulnerable():
    uploaded_file_url = None
    files = []

    upload_dir = current_app.config["UPLOAD_FOLDER"]

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            # VULNERABLE: No file type validation, no rename
            filename = file.filename  # Path traversal possible
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            uploaded_file_url = url_for("static", filename=f"uploads/{filename}")
            flash(f"File uploaded: {filename} (KHÔNG CÓ VALIDATION!)", "warning")

    # List uploaded files
    if os.path.exists(upload_dir):
        files = os.listdir(upload_dir)
        files = [f for f in files if f != ".gitkeep"]

    return render_template(
        "upload/vulnerable.html",
        uploaded_file_url=uploaded_file_url,
        files=files,
    )


@upload_bp.route("/secure", methods=["GET", "POST"])
def secure():
    uploaded_file_url = None
    files = []

    upload_dir = current_app.config["UPLOAD_FOLDER"]

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("File type không được phép! Chỉ chấp nhận: " + ", ".join(ALLOWED_EXTENSIONS), "error")
                return redirect(url_for("upload.secure"))

            # SECURE: Rename file with UUID, validate extension
            ext = file.filename.rsplit(".", 1)[1].lower()
            safe_filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(upload_dir, safe_filename)
            file.save(filepath)
            uploaded_file_url = url_for("upload.serve_file", filename=safe_filename)
            flash(f"File uploaded safely as: {safe_filename}", "success")

    if os.path.exists(upload_dir):
        files = os.listdir(upload_dir)
        files = [f for f in files if f != ".gitkeep"]

    return render_template(
        "upload/secure.html",
        uploaded_file_url=uploaded_file_url,
        files=files,
    )


@upload_bp.route("/serve/<filename>")
def serve_file(filename):
    """Serve uploaded files through the application (not direct static access)."""
    # Only serve allowed file types
    if not allowed_file(filename):
        abort(403)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


# --- IDOR Demo ---

@upload_bp.route("/vulnerable/profile/<int:user_id>")
@csrf.exempt
def vulnerable_profile(user_id):
    # VULNERABLE: No authorization check — any user can view any profile
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.email, u.role, u.balance,
                       p.bio, p.phone, p.address, p.ssn
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.id = %s
            """, (user_id,))
            profile = cursor.fetchone()
    finally:
        conn.close()

    if not profile:
        abort(404)

    return render_template("upload/idor_vulnerable.html", profile=profile, user_id=user_id)


@upload_bp.route("/secure/profile/<int:user_id>")
@login_required
def secure_profile(user_id):
    # SECURE: Authorization check — only own profile
    if current_user.id != user_id and current_user.role != "admin":
        flash("Bạn không có quyền xem profile này!", "error")
        abort(403)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.email, u.role,
                       p.bio, p.phone, p.address
                FROM users u
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE u.id = %s
            """, (user_id,))
            profile = cursor.fetchone()
    finally:
        conn.close()

    if not profile:
        abort(404)

    # SSN is deliberately excluded from the secure version
    return render_template("upload/idor_secure.html", profile=profile, user_id=user_id)
