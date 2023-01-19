from pydantic import BaseSettings
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parent

class Settings(BaseSettings):
    HOST: str
    PORT: int

    def __init__(self, root: Path) -> None:
        super().__init__(root / ".env")

settings = Settings(ROOT)