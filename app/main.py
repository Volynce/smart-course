from fastapi import FastAPI
from app.config import settings
from app.db import ping_db
from pydantic import BaseModel
from app.repositories.modules import list_modules
from app.repositories.tracks import list_tracks
from app.repositories.stages import list_stages
from app.repositories.articles import list_articles
from app.repositories.users import create_user
from app.repositories.users import get_user
from app.repositories.program import get_user_program

app = FastAPI(title="Smart Course API")

class UserCreateIn(BaseModel):
    email: str
    full_name: str
    track_id: str
    department: str | None = None
    position_title: str | None = None

@app.get("/health")
def health():
    return {"ok": True, "env": settings.app_env}
    
@app.get("/db-ping")
async def db_ping():
    ok = await ping_db()
    return {"db": ok}

@app.get("/modules")
async def get_modules(track_id: str | None = None):
    return await list_modules(track_id=track_id)

@app.get("/tracks")
async def get_tracks():
    return await list_tracks()

@app.get("/stages")
async def get_stages(track_id: str | None = None, rank: str | None = None):
    return await list_stages(track_id=track_id, rank=rank)

@app.get("/articles")
async def get_articles(module_id: str | None = None):
    return await list_articles(module_id=module_id)

@app.post("/users")
async def post_user(payload: UserCreateIn):
    return await create_user(
        email=payload.email,
        full_name=payload.full_name,
        track_id=payload.track_id,
        department=payload.department,
        position_title=payload.position_title,
    )

@app.get("/users/{user_id}")
async def get_user_by_id(user_id: str):
    return await get_user(user_id)

@app.get("/users/{user_id}/program")
async def get_program(user_id: str, stage_id: str | None = None):
    return await get_user_program(user_id=user_id, stage_id=stage_id)


