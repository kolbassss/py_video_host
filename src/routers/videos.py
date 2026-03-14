import pathlib
import uuid
import aiofiles
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.core.database import get_session
from src.models.all_models import Video, Channel, Like
from src.core.security import get_current_user_id

router = APIRouter(prefix="/videos", tags=["Videos"])

UPLOAD_DIR = pathlib.Path("media/videos")
THUMB_DIR = pathlib.Path("media/thumbnails")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_video(
    channel_id: uuid.UUID = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    video_file: UploadFile = File(...),
    thumbnail_file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    channel = await session.scalar(select(Channel).where(Channel.id == channel_id, Channel.owner_id == user_id))
    if not channel:
        raise HTTPException(status_code=403, detail="You do not own this channel")

    video_ext = pathlib.Path(video_file.filename).suffix.lower()
    thumb_ext = pathlib.Path(thumbnail_file.filename).suffix.lower()
    video_id = uuid.uuid4()
    
    video_path = UPLOAD_DIR / f"{video_id}{video_ext}"
    thumb_path = THUMB_DIR / f"{video_id}{thumb_ext}"
    
    async with aiofiles.open(video_path, "wb") as f:
        while chunk := await video_file.read(1024 * 1024):
            await f.write(chunk)
            
    async with aiofiles.open(thumb_path, "wb") as f:
        await f.write(await thumbnail_file.read())

    new_video = Video(id=video_id, title=title, description=description, file_path=str(video_path), thumbnail_path=str(thumb_path), channel_id=channel.id)
    session.add(new_video)
    await session.commit()
    return {"video_id": video_id}

@router.get("/{video_id}/watch")
async def watch_video(video_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    video = await session.scalar(select(Video).where(Video.id == video_id))
    if not video:
        raise HTTPException(404, "Video not found")
    
    video.views += 1
    likes_count = await session.scalar(select(func.count(Like.id)).where(Like.video_id == video_id))
    await session.commit()
    
    return {
        "title": video.title, 
        "description": video.description, 
        "views": video.views, 
        "likes": likes_count or 0,
        "video_url": f"/videos/stream/{video.id}"
    }

@router.get("/stream/{video_id}")
async def stream_video(video_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    video = await session.scalar(select(Video).where(Video.id == video_id))
    return FileResponse(video.file_path, media_type="video/mp4")

@router.post("/{video_id}/like")
async def toggle_like(video_id: uuid.UUID, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_session)):
    like = await session.scalar(select(Like).where(Like.user_id == user_id, Like.video_id == video_id))
    if like:
        await session.delete(like)
        msg = "Like removed"
    else:
        session.add(Like(user_id=user_id, video_id=video_id))
        msg = "Like added"
    await session.commit()
    return {"message": msg}
