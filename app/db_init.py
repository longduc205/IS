import pymysql
from werkzeug.security import generate_password_hash


def init_db(app):
    """Initialize database tables and seed data."""
    conn = pymysql.connect(
        host=app.config["DATABASE_HOST"],
        port=app.config["DATABASE_PORT"],
        user=app.config["DATABASE_USER"],
        password=app.config["DATABASE_PASSWORD"],
        database=app.config["DATABASE_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

    try:
        with conn.cursor() as cursor:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(120),
                    role VARCHAR(20) DEFAULT 'user',
                    balance DECIMAL(10,2) DEFAULT 1000.00
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Posts table (for XSS demo)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    title VARCHAR(200),
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Profiles table (for IDOR demo)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT UNIQUE,
                    bio TEXT,
                    phone VARCHAR(20),
                    address VARCHAR(255),
                    ssn VARCHAR(20),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Transfer logs (for CSRF demo)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transfers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    from_user_id INT,
                    to_username VARCHAR(80),
                    amount DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_user_id) REFERENCES users(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Seed data if empty
            cursor.execute("SELECT COUNT(*) as cnt FROM users")
            if cursor.fetchone()["cnt"] == 0:
                seed_users = [
                    ("admin", "admin123", "admin@vulnlab.local", "admin", 5000.00),
                    ("alice", "alice123", "alice@vulnlab.local", "user", 1000.00),
                    ("bob", "bob123", "bob@vulnlab.local", "user", 2500.00),
                    ("charlie", "charlie123", "charlie@company.com", "user", 800.00),
                    ("attacker", "hack3r", "evil@hacker.com", "user", 0.00),
                ]

                for username, password, email, role, balance in seed_users:
                    pw_hash = generate_password_hash(password)
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, email, role, balance) VALUES (%s, %s, %s, %s, %s)",
                        (username, pw_hash, email, role, balance),
                    )

                # Seed profiles
                profiles = [
                    (1, "System administrator", "0900-000-001", "123 Admin St", "111-22-3333"),
                    (2, "Software developer at TechCorp", "0900-000-002", "456 Dev Lane", "444-55-6666"),
                    (3, "Project manager", "0900-000-003", "789 Mgr Blvd", "777-88-9999"),
                    (4, "QA Engineer", "0900-000-004", "321 Test Ave", "222-33-4444"),
                    (5, "Penetration tester", "0900-000-005", "N/A", "N/A"),
                ]

                for user_id, bio, phone, address, ssn in profiles:
                    cursor.execute(
                        "INSERT INTO profiles (user_id, bio, phone, address, ssn) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, bio, phone, address, ssn),
                    )

                # Seed posts
                posts = [
                    (1, "Welcome to VulnLab", "This is a demo platform for web security testing."),
                    (2, "My First Post", "Hello everyone! I'm Alice."),
                    (3, "Project Update", "The new feature is ready for review."),
                ]

                for user_id, title, content in posts:
                    cursor.execute(
                        "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
                        (user_id, title, content),
                    )

                print("[+] Database seeded successfully")
            else:
                print("[*] Database already has data, skipping seed")

    finally:
        conn.close()
