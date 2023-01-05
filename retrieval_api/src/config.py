from pydantic import BaseSettings
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parent.parent

class Settings(BaseSettings):
    HOST: str
    PORT: int

    class Config:
        env_file = ROOT / ".env"

settings = Settings()