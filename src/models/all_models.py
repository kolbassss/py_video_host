import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.core.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    dob: Mapped[datetime.date]
    password: Mapped[bytes]
    created_at: Mapped[datetime.datetime] = mapped_column(default=lambda: datetime.datetime.now(datetime.UTC))
    channels: Mapped[list["Channel"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    likes: Mapped[list["Like"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Channel(Base):
    __tablename__ = "channels"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    description: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    owner: Mapped["User"] = relationship(back_populates="channels")
    videos: Mapped[list["Video"]] = relationship(back_populates="channel", cascade="all, delete-orphan")

class Video(Base):
    __tablename__ = "videos"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    description: Mapped[str]
    file_path: Mapped[str]
    thumbnail_path: Mapped[str]
    views: Mapped[int] = mapped_column(default=0)
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"))
    channel: Mapped["Channel"] = relationship(back_populates="videos")
    likes: Mapped[list["Like"]] = relationship(back_populates="video", cascade="all, delete-orphan")

class Like(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("videos.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="likes")
    video: Mapped["Video"] = relationship(back_populates="likes")
