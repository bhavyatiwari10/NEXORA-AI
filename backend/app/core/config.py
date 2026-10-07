from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "Nexora AI"
    environment: str = "development"
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./nexora.db"
    llm_provider: str = "mock"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_model: str = 'gpt-4o-mini'
    anthropic_model: str = 'claude-3-5-haiku-latest'
    seller_name: str = "Nexora Demo Store"
    seller_gstin: str = "09ABCDE1234F1Z5"
    seller_state: str = "Uttar Pradesh"
    low_confidence_threshold: float = .72
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
settings = Settings()
