# 🛡️ VulnLab — Web Application Security Demo

> **⚠️ CẢNH BÁO: Dự án này chứa code có chủ đích vulnerable. Chỉ sử dụng cho mục đích giáo dục. KHÔNG triển khai trên môi trường production!**

VulnLab là nền tảng mô phỏng các lỗ hổng bảo mật web phổ biến nhất, xây dựng trên Flask + MySQL + Docker. Mỗi attack type đều có phiên bản **Vulnerable** (để demo tấn công) và **Secure** (để hiểu cách phòng chống).

---

## 📋 Mục lục

1. [Web Application là gì?](#1-web-application-là-gì)
2. [Các loại tấn công](#2-các-loại-tấn-công)
3. [Demo thực tế](#3-demo-thực-tế)
4. [Phân tích lỗ hổng](#4-phân-tích-lỗ-hổng)
5. [Cách phòng chống](#5-cách-phòng-chống)
6. [Kết luận](#6-kết-luận)
7. [Cài đặt & Chạy](#7-cài-đặt--chạy)

---

## 1. Web Application là gì?

Web application là ứng dụng chạy trên trình duyệt, giao tiếp với server qua HTTP/HTTPS. Ví dụ: Gmail, Facebook, ngân hàng online...

### Vì sao dễ bị tấn công?

- **90% ứng dụng web** đều nhận input từ user → dễ bị exploit
- HTTP là giao thức **stateless** → phải dùng cookie/session → dễ bị đánh cắp
- Business logic phức tạp → nhiều điểm yếu
- Third-party dependencies → supply chain risk

---

## 2. Các loại tấn công

### 🔴 SQL Injection (SQLi)
Chèn mã SQL độc hại vào input để **đọc, sửa, xóa** dữ liệu database.

| Severity | OWASP Rank | Prevalence |
|----------|-----------|------------|
| **Critical** | #3 (2021) | Rất phổ biến |

### 🔴 Cross-Site Scripting (XSS)
Chèn JavaScript vào trang web để **đánh cắp cookie**, session hijacking, phishing.

| Severity | OWASP Rank | Prevalence |
|----------|-----------|------------|
| **High** | #7 (2021) | Rất phổ biến |

### 🔴 Cross-Site Request Forgery (CSRF)
Lừa user đã đăng nhập thực hiện hành động **không mong muốn** (chuyển tiền, đổi password).

| Severity | OWASP Rank | Prevalence |
|----------|-----------|------------|
| **High** | Top 10 | Phổ biến |

### 🔴 File Upload & IDOR
Upload file độc hại hoặc **truy cập trái phép** tài nguyên user khác.

| Severity | OWASP Rank | Prevalence |
|----------|-----------|------------|
| **High** | #1 (2021) - Broken Access Control | Rất phổ biến |

---

## 3. Demo thực tế

### Khởi chạy
```bash
docker-compose up -d --build
```
Truy cập: **http://localhost:5000**

### Tài khoản demo
| Username | Password | Role | Balance |
|----------|----------|------|---------|
| admin | admin123 | Admin | $5,000 |
| alice | alice123 | User | $1,000 |
| bob | bob123 | User | $2,500 |
| charlie | charlie123 | User | $800 |
| attacker | hack3r | User | $0 |

### Demo SQL Injection
```
URL: http://localhost:5000/sqli/vulnerable?search=' OR '1'='1
Kết quả: Trả về TẤT CẢ users trong database!

URL: http://localhost:5000/sqli/vulnerable?search=' UNION SELECT id, username, password_hash, email, role, balance FROM users--
Kết quả: Lấy cả PASSWORD HASH!
```

### Demo XSS
```
1. Vào http://localhost:5000/xss/vulnerable
2. Đăng bài với content: <script>alert('XSS!')</script>
3. Bài viết hiển thị → JavaScript chạy ngay trên browser mọi người!
```

### Demo CSRF
```
1. Đăng nhập tài khoản alice (alice123)
2. Mở file attacker/csrf_attack.html trong browser
3. Page tự động chuyển $500 từ alice → attacker!
```

### Demo IDOR
```
URL: http://localhost:5000/upload/vulnerable/profile/1  → Admin profile + SSN!
URL: http://localhost:5000/upload/vulnerable/profile/2  → Alice profile + SSN!
→ Không cần đăng nhập, chỉ cần đổi ID!
```

---

## 4. Phân tích lỗ hổng

### SQL Injection
**Nguyên nhân:**
- Không validate/sanitize input
- Query nối chuỗi trực tiếp: `f"SELECT * FROM users WHERE username = '{input}'"`
- Database user có quá nhiều quyền

**Code vulnerable:**
```python
# ❌ String concatenation
query = f"SELECT * FROM users WHERE username = '{search}'"
cursor.execute(query)
```

### XSS
**Nguyên nhân:**
- Render HTML trực tiếp từ user input
- Sử dụng `| safe` trong template engine
- Không có Content-Security-Policy header

### CSRF
**Nguyên nhân:**
- Không có CSRF token trong form
- Không verify Referer/Origin header
- Cookie không có SameSite attribute

### File Upload & IDOR
**Nguyên nhân:**
- Không validate file extension
- Giữ original filename (path traversal)
- Không kiểm tra authorization

---

## 5. Cách phòng chống

### SQL Injection
```python
# ✅ Parameterized Query
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (search,))

# ✅ ORM (SQLAlchemy)
User.query.filter_by(username=search).first()
```

### XSS
```python
# ✅ Sanitize HTML
import bleach
clean_content = bleach.clean(user_input)

# ✅ CSP Header
Content-Security-Policy: default-src 'self'; script-src 'self'

# ✅ Jinja2 auto-escape (default)
{{ content }}  <!-- auto-escaped -->
```

### CSRF
```html
<!-- ✅ CSRF Token -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

<!-- ✅ SameSite Cookie -->
Set-Cookie: session=abc123; SameSite=Lax; HttpOnly; Secure
```

### File Upload & IDOR
```python
# ✅ Whitelist extensions
ALLOWED = {"png", "jpg", "jpeg", "gif"}

# ✅ Rename file
safe_name = f"{uuid4().hex}.{ext}"

# ✅ Authorization check
if current_user.id != user_id:
    abort(403)
```

---

## 6. Kết luận

- Web application attack **rất phổ biến** — 90%+ ứng dụng có lỗ hổng
- Hầu hết lỗ hổng đều do **không validate input** từ user
- Cần áp dụng **Secure Coding** từ giai đoạn development
- **Defense in Depth**: nhiều lớp bảo vệ, không chỉ 1
- Security testing (Pentest, SAST, DAST) là **bắt buộc**

---

## 7. Cài đặt & Chạy

### Yêu cầu
- Docker & Docker Compose

### Quick Start
```bash
# Clone repo
git clone <repo-url>
cd IS

# Khởi chạy
docker-compose up -d --build

# Truy cập
open http://localhost:5000

# Dừng
docker-compose down

# Dừng + xóa data
docker-compose down -v
```

### Cấu trúc dự án
```
IS/
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Flask app container
├── requirements.txt        # Python dependencies
├── run.py                  # Entry point
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── config.py           # Database connection
│   ├── models.py           # User model
│   ├── db_init.py          # Database seeding
│   ├── routes/
│   │   ├── auth.py         # Login/Register
│   │   ├── sqli.py         # SQL Injection demo
│   │   ├── xss.py          # XSS demo
│   │   ├── csrf_demo.py    # CSRF demo
│   │   └── upload.py       # File Upload + IDOR demo
│   ├── templates/          # Jinja2 templates
│   └── static/             # CSS, JS, uploads
└── attacker/
    └── csrf_attack.html    # CSRF attack simulation
```

### Tech Stack
- **Backend:** Python Flask 3.1
- **Database:** MySQL 8.0
- **Frontend:** Jinja2 + Vanilla CSS/JS
- **Container:** Docker Compose

---

## 📚 Tham khảo

- [OWASP Top 10 (2021)](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [DVWA - Damn Vulnerable Web Application](https://github.com/digininja/DVWA)

---

## ⚖️ License

Dự án này chỉ dành cho mục đích **giáo dục**. Tác giả không chịu trách nhiệm cho bất kỳ việc sử dụng sai mục đích nào.