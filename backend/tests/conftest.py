import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-production")
os.environ.setdefault("AUTHENTICATOR_API_KEY", "test-api-key-not-production")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/auther")
os.environ.setdefault("PUBLIC_APP_URL", "http://localhost:5173")
os.environ.setdefault("REDIRECT_ALLOWLIST", "http://localhost:5173,http://localhost:5174")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("SMTP_HOST", "")
