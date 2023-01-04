from pydantic import BaseSettings

class Settings(BaseSettings):
    HOST: str
    PORT: int

    class Config:
        env_file = ".env"

settings = Settings()