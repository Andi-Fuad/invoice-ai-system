from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    gemini_flash_3: str
    upload_dir: str = "./uploads"
    report_dir: str = "./reports"
    
    class Config:
        env_file = ".env"

settings = Settings()