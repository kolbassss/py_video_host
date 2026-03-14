from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent.parent

class AuthData(BaseModel):
    private_key: Path = BASE_DIR / "src" / "auth" / "tokens" / "private_key.pem"
    public_key: Path = BASE_DIR / "src" / "auth" / "tokens" / "public_key.pem"
    algorithm: str = "RS256"
    days: int = 7

class Config(BaseModel):
    auth_data: AuthData = AuthData()

config = Config()
