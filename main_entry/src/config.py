from pydantic import BaseSettings
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parent.parent
RETRIEVAL_API_ROOT = ROOT.parent / "retrieval_api"
TRY_ON_API_ROOT = ROOT.parent / "tryon_api"

class Settings(BaseSettings):
    HOST: str
    PORT: int

    def __init__(self, root: Path) -> None:
        super().__init__(root / ".env")


settings = Settings(ROOT)
retrieval_settings = Settings(RETRIEVAL_API_ROOT)
tryon_settings = Settings(TRY_ON_API_ROOT)