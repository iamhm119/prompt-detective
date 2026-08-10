"""
Configuration settings with environment variables
"""
import os
from typing import Optional, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "Prompt Detective API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/prompt_detective")
    DB_SSL_MODE: str = os.getenv("DB_SSL_MODE", "require")
    DB_POOL_ENABLED: bool = os.getenv("DB_POOL_ENABLED", "true").lower() == "true"
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "0"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "300"))
    DB_PRE_PING: bool = os.getenv("DB_PRE_PING", "true").lower() == "true"
    DB_STATEMENT_TIMEOUT_MS: int = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000"))
    DB_CONNECT_RETRIES: int = int(os.getenv("DB_CONNECT_RETRIES", "3"))
    DB_RETRY_INITIAL_DELAY: float = float(os.getenv("DB_RETRY_INITIAL_DELAY", "1.5"))
    DB_RETRY_BACKOFF_FACTOR: float = float(os.getenv("DB_RETRY_BACKOFF_FACTOR", "2.0"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    PUBLIC_API_BASE_URL: str = os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8000")
    CLOUDINARY_CLOUD_NAME: Optional[str] = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: Optional[str] = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: Optional[str] = os.getenv("CLOUDINARY_API_SECRET")
    
    # API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct")
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Email Service (Gmail SMTP)
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "gmail")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "tryreverseai@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "tryreverseai@gmail.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Reverse AI")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "tryreverseai@gmail.com")
    
    # Brevo/Sendinblue API (FREE 300 emails/day, no domain verification needed)
    BREVO_API_KEY: Optional[str] = os.getenv("BREVO_API_KEY")
    
    # Resend API (requires domain verification)
    RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY")
    
    # Razorpay Payment Gateway (Indian market - UPI, Cards, NetBanking, Wallets)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    
    # Frontend URL (for email links and OAuth redirects)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,https://your-frontend-domain.com"
    )

    # Admin bootstrap
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "tryreverseai@gmail.com")
    ADMIN_PASSWORD: Optional[str] = os.getenv("ADMIN_PASSWORD")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMe!123!")
    
    @staticmethod
    def _strip_optional(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip()

    @staticmethod
    def _collapse_secret(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return "".join(value.split())

    @staticmethod
    def _sanitize_oauth_value(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip().strip('"').strip("'")
        return cleaned or None

    def model_post_init(self, __context: Any) -> None:  # type: ignore[override]
        """Normalize secrets that are sensitive to whitespace characters."""
        provider = (self.EMAIL_PROVIDER or "").lower()

        if self.SMTP_USERNAME:
            self.SMTP_USERNAME = self.SMTP_USERNAME.strip()

        if self.SMTP_PASSWORD:
            cleaned = self.SMTP_PASSWORD.strip()
            if provider in {"gmail", "google"}:
                cleaned = self._collapse_secret(cleaned)
            self.SMTP_PASSWORD = cleaned

        if self.EMAIL_FROM_ADDRESS:
            self.EMAIL_FROM_ADDRESS = self.EMAIL_FROM_ADDRESS.strip()

        if self.SUPPORT_EMAIL:
            self.SUPPORT_EMAIL = self.SUPPORT_EMAIL.strip()

        if self.BREVO_API_KEY:
            self.BREVO_API_KEY = self._collapse_secret(self.BREVO_API_KEY.strip())

        if self.RESEND_API_KEY:
            self.RESEND_API_KEY = self._collapse_secret(self.RESEND_API_KEY.strip())

        if self.SECRET_KEY:
            self.SECRET_KEY = self.SECRET_KEY.strip()

        # Normalize Google OAuth credentials and allow fallback env names
        google_client_sources = (
            self.GOOGLE_CLIENT_ID,
            os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
            os.getenv("VITE_GOOGLE_CLIENT_ID"),
        )
        for value in google_client_sources:
            sanitized = self._sanitize_oauth_value(value)
            if sanitized:
                self.GOOGLE_CLIENT_ID = sanitized
                break

        google_secret_sources = (
            self.GOOGLE_CLIENT_SECRET,
            os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        )
        for value in google_secret_sources:
            sanitized = self._sanitize_oauth_value(value)
            if sanitized:
                self.GOOGLE_CLIENT_SECRET = sanitized
                break

    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def cloud_storage_configured(self) -> bool:
        """Return True if Cloudinary credentials are present."""
        return all(
            [
                self.CLOUDINARY_CLOUD_NAME,
                self.CLOUDINARY_API_KEY,
                self.CLOUDINARY_API_SECRET,
            ]
        )
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file

settings = Settings()