"""Configuration management for TranscribeMe service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Twilio Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # OpenAI Configuration
    openai_api_key: str

    # Service Configuration
    base_url: str = "http://localhost:8000"
    database_url: str = "sqlite:///transcribeme.db"

    # Security Settings
    secret_key: str = "dev-secret-key-change-in-production"
    transcript_expiry_days: int = 7
    max_call_duration_seconds: int = 300

    # Phone Number Validation
    allowed_country_codes: list[str] = ["+64"]  # New Zealand only

    # Development Settings
    debug: bool = True
    log_level: str = "INFO"
    console_log_level: str = "DEBUG"  # Console always at debug level

    # Test Configuration
    test_mobile_number: str = "+64210822348"  # For SMS testing

    model_config = {"env_file": ".env", "case_sensitive": False}


# Global settings instance
settings = Settings()
