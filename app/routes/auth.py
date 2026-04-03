from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Vui lòng nhập đầy đủ thông tin.", "error")
            return render_template("auth/login.html")

        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash(f"Chào mừng {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        flash("Tên đăng nhập hoặc mật khẩu không đúng.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip()

        if not username or not password:
            flash("Vui lòng nhập đầy đủ thông tin.", "error")
            return render_template("auth/register.html")

        if len(username) < 3 or len(username) > 80:
            flash("Username phải từ 3-80 ký tự.", "error")
            return render_template("auth/register.html")

        if User.get_by_username(username):
            flash("Username đã tồn tại.", "error")
            return render_template("auth/register.html")

        User.create(username, password, email)
        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("main.index"))
