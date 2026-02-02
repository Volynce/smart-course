from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="Smart Course API")

@app.get("/health")
def health():
    return {"ok": True, "env": settings.app_env}
