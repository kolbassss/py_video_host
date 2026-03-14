from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.database import get_session
from src.models.all_models import User, Channel
from src.schemas.schemas import UserCreate, UserLogin, PasswordRecover, ProfileResponse
from src.core.security import hash_password, check_password, create_access_token, get_current_user_id

router = APIRouter(prefix="/auth", tags=["Auth & Profile"])

@router.post("/register")
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    existing = await session.scalar(select(User).where(User.username == user_data.username))
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=user_data.username, dob=user_data.dob, password=hash_password(user_data.password))
    session.add(new_user)
    await session.commit()
    return {"message": "Success"}

@router.post("/login")
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.username == data.username))
    if not user or not check_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": await create_access_token(user.id)}

@router.post("/recover-password")
async def recover_password(data: PasswordRecover, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.username == data.username, User.dob == data.dob))
    if not user:
        raise HTTPException(status_code=403, detail="Verification failed")
    user.password = hash_password(data.new_password)
    await session.commit()
    return {"message": "Password updated successfully"}

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.id == user_id))
    channels_count = await session.scalar(select(func.count(Channel.id)).where(Channel.owner_id == user_id))
    return {"username": user.username, "dob": user.dob, "channels_count": channels_count or 0}
