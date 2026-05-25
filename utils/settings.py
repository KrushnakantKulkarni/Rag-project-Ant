from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4o-mini"
    DATABASE_PATH: str = "traces.db"
    TRACE_ARCHIVE_DIR: str = "traces/"
    API_KEY_SECRET: str
    
    class Config:
        env_file = ".env"

# Instantiate global settings object for codebase imports
settings = Settings()
