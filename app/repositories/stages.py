from typing import List, Dict
from sqlalchemy import text
from app.db import engine

async def list_stages(track_id: str | None = None, rank: str | None = None) -> List[Dict]:
    where = []
    params: dict = {}

    if track_id:
        where.append("track_id = :track_id")
        params["track_id"] = track_id

    if rank:
        where.append("rank = :rank")
        params["rank"] = rank

    where_sql = ""
    if where:
        where_sql = "WHERE " + " AND ".join(where)

    q = text(f"""
        SELECT
          id::text AS id,
          track_id::text AS track_id,
          rank,
          level
        FROM urovni
        {where_sql}
        ORDER BY rank, level
    """)

    async with engine.connect() as conn:
        res = await conn.execute(q, params)
        rows = res.mappings().all()

    return [dict(r) for r in rows]
