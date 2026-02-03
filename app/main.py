from fastapi import FastAPI
from app.config import settings
from app.db import ping_db
from pydantic import BaseModel
from typing import List
from app.repositories.modules import list_modules
from app.repositories.tracks import list_tracks
from app.repositories.stages import list_stages
from app.repositories.articles import list_articles
from app.repositories.users import create_user
from app.repositories.users import get_user
from app.repositories.minitest import get_article_minitest
from app.repositories.minitest_submit import submit_minitest
from app.repositories.admission import stage_admission
from app.repositories.entry_diagnostic import entry_start
from app.repositories.entry_submit import entry_submit
from app.repositories.program import generate_program_for_active_stage, get_program

app = FastAPI(title="Smart Course API")

class UserCreateIn(BaseModel):
    email: str
    full_name: str
    track_id: str
    department: str | None = None
    position_title: str | None = None

class MiniTestAnswerIn(BaseModel):
    question_id: str
    selected_option_id: str

class MiniTestSubmitIn(BaseModel):
    article_id: str
    answers: list[MiniTestAnswerIn]

class EntryAnswer(BaseModel):
    question_id: str
    selected_option_id: str

class EntrySubmitIn(BaseModel):
    diagnostika_id: str
    answers: List[EntryAnswer]

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

@app.get("/articles/{article_id}/minitest")
async def article_minitest(article_id: str):
    return await get_article_minitest(article_id)

@app.post("/users/{user_id}/minitest/submit")
async def user_minitest_submit(user_id: str, payload: MiniTestSubmitIn):
    answers = [{"question_id": a.question_id, "selected_option_id": a.selected_option_id} for a in payload.answers]
    return await submit_minitest(user_id=user_id, article_id=payload.article_id, answers=answers)

@app.get("/users/{user_id}/stage-admission")
async def get_stage_admission(user_id: str):
    return await stage_admission(user_id)

@app.post("/diagnostics/entry/start")
async def diagnostics_entry_start(user_id: str):
    return await entry_start(user_id=user_id)

@app.post("/diagnostics/entry/submit")
async def diagnostics_entry_submit(payload: EntrySubmitIn):
    return await entry_submit(
        diagnostika_id=payload.diagnostika_id,
        answers=[a.model_dump() for a in payload.answers],
    )

@app.post("/users/{user_id}/program/generate")
async def program_generate(user_id: str):
    return await generate_program_for_active_stage(user_id)

@app.get("/users/{user_id}/program")
async def program_get(user_id: str, stage_id: str | None = None):
    return await get_program(user_id, stage_id=stage_id)


