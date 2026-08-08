import os

os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("JWT_REFRESH_SECRET_KEY", "test-refresh-secret")
os.environ.setdefault("SESSION_SECRET_KEY", "test-session-secret")
os.environ.setdefault("MAIL_SERVER", "localhost")
os.environ.setdefault("MAIL_PORT", "1025")
os.environ.setdefault("MAIL_USERNAME", "test")
os.environ.setdefault("MAIL_PASSWORD", "test")
os.environ.setdefault("MAIL_DEFAULT_SENDER", "test@example.com")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
