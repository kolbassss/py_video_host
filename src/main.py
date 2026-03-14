from fastapi import FastAPI
from src.core.database import Base, engine
from src.routers.auth import router as auth_router
from src.routers.channels import router as channels_router
from src.routers.videos import router as videos_router

app = FastAPI(title="PyVideoHost")

app.include_router(auth_router)
app.include_router(channels_router)
app.include_router(videos_router)

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        from src.models import all_models 
        await conn.run_sync(Base.metadata.create_all)
