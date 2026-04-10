# Kiến thức quan trọng về Codebase VulnLab (An toàn thông tin)

Tài liệu này tổng hợp các kiến thức cốt lõi về cấu trúc dự án và các lỗ hổng bảo mật được mô phỏng trong codebase này.

## 1. Tổng quan kiến trúc
- **Framework**: Flask (Python).
- **Cấu trúc**: Modular Pattern sử dụng **Blueprints**.
  - `app/__init__.py`: Khởi tạo ứng ứng dụng, cấu hình LoginManager và CSRFProtect.
  - `app/routes/`: Chứa logic xử lý cho từng lỗ hổng riêng biệt.
  - `app/db_init.py`: Tự động khởi tạo database MySQL với dữ liệu mẫu (Seeding).
- **Database**: Sử dụng thư viện `pymysql` để kết nối trực tiếp với MySQL (thay vì dùng ORM như SQLAlchemy để dễ dàng mô phỏng SQL Injection).
- **Deployment**: Dockerized (`Dockerfile` và `docker-compose.yml`).

---

## 2. Các lỗ hổng bảo mật & Cách khắc phục

### A. SQL Injection (SQLi)
*Địa điểm: `app/routes/sqli.py`*

- **Vulnerable**: Sử dụng f-string hoặc cộng chuỗi trực tiếp vào SQL query.
  - `query = f"SELECT ... WHERE username = '{search}'"`
- **Secure**: Sử dụng **Parameterized Queries** (Prepared Statements).
  - `query = "SELECT ... WHERE username = %s"`
  - `cursor.execute(query, (search,))`

### B. Cross-Site Scripting (XSS)
*Địa điểm: `app/routes/xss.py`*

- **Vulnerable**: Lưu trữ dữ liệu người dùng nhập vào DB (`Stored XSS`) và hiển thị trực tiếp lên template mà không qua bộ lọc.
- **Secure**: 
  - **Sanitization**: Sử dụng thư viện `bleach` để làm sạch HTML trước khi lưu.
  - **Security Headers**: Thiết lập `Content-Security-Policy` (CSP) để chặn inline-scripts không an toàn.
  - **Template Escaping**: Jinja2 tự động escape nhưng trong demo này, phiên bản lỗi thường dùng tag `|safe` (cần tránh lạm dụng tag này).

### C. Cross-Site Request Forgery (CSRF)
*Địa điểm: `app/routes/csrf_demo.py`*

- **Vulnerable**: Route xử lý hành động quan trọng (như chuyển tiền) không kiểm tra token CSRF.
  - Sử dụng `@csrf.exempt` để tắt bảo vệ trong demo.
- **Secure**: 
  - Sử dụng `Flask-WTF` (CSRFProtect).
  - Tự động kiểm tra token qua Request Header hoặc Form dữ liệu.

### D. File Upload & IDOR
*Địa điểm: `app/routes/upload.py`*

- **Lỗi File Upload**: Lưu file với tên gốc (`file.filename`) và không kiểm tra phần mở rộng (extension).
  - **Khắc phục**: Đổi tên file thành UUID, kiểm tra whitelist extension, phục vụ file qua một route trung gian (`serve_file`) thay vì truy cập trực tiếp thư mục tĩnh.
- **Insecure Direct Object Reference (IDOR)**: Truy cập profile user qua ID (`/profile/<int:user_id>`) mà không kiểm tra quyền sở hữu.
  - **Khắc phục**: Luôn kiểm tra `current_user.id == user_id` trước khi truy vấn dữ liệu nhạy cảm.

---

## 3. Một số thành phần đặc biệt
- **`app/db_init.py`**: Chứa các SQL scripts tạo bảng `users`, `posts`, `transfers`, `profiles`. Đây là nơi quan sát cấu trúc dữ liệu của dự án.
- **`attacker/`**: Chứa các file HTML mẫu để thực hiện tấn công CSRF hoặc XSS (External payloads).
- **`app/templates/base.html`**: File giao diện gốc, sử dụng hệ thống icons từ `app/static/icons/`.

---

> [!IMPORTANT]
> Dự án này được thiết kế cho mục đích học tập. **Tuyệt đối không** sử dụng các pattern trong file `vulnerable` cho các dự án thực tế.
