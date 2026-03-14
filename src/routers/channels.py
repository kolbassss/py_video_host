from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_session
from src.models.all_models import Channel
from src.schemas.schemas import ChannelCreate
from src.core.security import get_current_user_id

router = APIRouter(prefix="/channels", tags=["Channels"])

@router.post("/create")
async def create_channel(data: ChannelCreate, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_session)):
    channel = Channel(title=data.title, description=data.description, owner_id=user_id)
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return {"channel_id": channel.id, "title": channel.title}
