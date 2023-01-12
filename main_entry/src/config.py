from pydantic import BaseSettings
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parent.parent

class Settings(BaseSettings):
    HOST: str
    PORT: int
    HOST_RETRIEVAL: str
    PORT_RETRIEVAL: int
    HOST_TRYON: str
    PORT_TRYON: int

    def __init__(self, root: Path) -> None:
        super().__init__(root / ".env")


settings = Settings(ROOT)