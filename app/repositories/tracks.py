from typing import List, Dict
from sqlalchemy import text
from app.db import engine

async def list_tracks() -> List[Dict]:
    q = text("""
        SELECT id::text AS id, name
        FROM treki
        ORDER BY name
    """)
    async with engine.connect() as conn:
        res = await conn.execute(q)
        rows = res.mappings().all()
    return [dict(r) for r in rows]
