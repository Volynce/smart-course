from typing import List, Dict
from sqlalchemy import text
from app.db import engine

async def get_user_program(user_id: str, stage_id: str | None = None) -> List[Dict]:
    # Если stage_id не передан — берём активный stage пользователя
    if stage_id is None:
        q = text("""
            SELECT
              p.article_id::text AS article_id,
              p.stage_id::text AS stage_id,
              p.is_required,
              p.minitest_passed,
              a.title,
              a.content,
              a.module_id::text AS module_id
            FROM progress_urovney_polzovatelya sp
            JOIN programma_polzovatelya p
              ON p.user_id = sp.user_id AND p.stage_id = sp.stage_id
            JOIN stati a
              ON a.id = p.article_id
            WHERE sp.user_id = CAST(:user_id AS uuid)
              AND sp.status = 'active'
            ORDER BY a.title
        """)
        params = {"user_id": user_id}
    else:
        q = text("""
            SELECT
              p.article_id::text AS article_id,
              p.stage_id::text AS stage_id,
              p.is_required,
              p.minitest_passed,
              a.title,
              a.content,
              a.module_id::text AS module_id
            FROM programma_polzovatelya p
            JOIN stati a ON a.id = p.article_id
            WHERE p.user_id = CAST(:user_id AS uuid)
              AND p.stage_id = CAST(:stage_id AS uuid)
            ORDER BY a.title
        """)
        params = {"user_id": user_id, "stage_id": stage_id}

    async with engine.connect() as conn:
        res = await conn.execute(q, params)
        rows = res.mappings().all()

    return [dict(r) for r in rows]
