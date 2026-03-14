from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Создаем движок SQLite (файл db.sqlite3 появится в корне)
engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3", echo=True)

# Фабрика сессий
SessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass

# Dependency для FastAPI
async def get_session():
    async with SessionLocal() as session:
        yield session
