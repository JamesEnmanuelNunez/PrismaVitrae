from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "PrismaVitae"
    APP_ENV: str = "development"

    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str = ""

    GEMINI_API_KEY: str

    DATABASE_URL: str


settings = Settings()
