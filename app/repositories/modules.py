from typing import List, Dict
from sqlalchemy import text
from app.db import engine

async def list_modules(track_id: str | None = None) -> List[Dict]:
    if track_id:
        q = text("""
            SELECT id::text AS id, track_id::text AS track_id, name
            FROM moduli
            WHERE track_id = :track_id
            ORDER BY name
        """)
        params = {"track_id": track_id}
    else:
        q = text("""
            SELECT id::text AS id, track_id::text AS track_id, name
            FROM moduli
            ORDER BY name
        """)
        params = {}

    async with engine.connect() as conn:
        res = await conn.execute(q, params)
        rows = res.mappings().all()
    return [dict(r) for r in rows]
