from fastapi import FastAPI
from app.config import settings
from app.db import ping_db
from app.repositories.modules import list_modules

app = FastAPI(title="Smart Course API")

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
