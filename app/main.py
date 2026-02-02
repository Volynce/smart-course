from fastapi import FastAPI
from app.config import settings
from app.db import ping_db

app = FastAPI(title="Smart Course API")

@app.get("/health")
def health():
    return {"ok": True, "env": settings.app_env}
    
@app.get("/db-ping")
async def db_ping():
    ok = await ping_db()
    return {"db": ok}
