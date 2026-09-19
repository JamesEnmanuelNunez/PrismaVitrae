from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "PrismaVitae"
    APP_ENV: str = "development"

    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str = ""

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.5-flash"

    STORAGE_BUCKET: str = "cvs"
    MAX_UPLOAD_MB: int = 10

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://prismavitae.netlify.app",
    ]


settings = Settings()