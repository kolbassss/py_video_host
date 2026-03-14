import datetime
import bcrypt
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.config import config

bearer = HTTPBearer()

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), salt=bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

async def create_access_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=config.auth_data.days)
    }
    return jwt.encode(payload, config.auth_data.private_key.read_text(), algorithm=config.auth_data.algorithm)

async def get_current_user_id(token: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    try:
        payload = jwt.decode(token.credentials, config.auth_data.public_key.read_text(), algorithms=[config.auth_data.algorithm])
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
