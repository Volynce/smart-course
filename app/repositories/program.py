from typing import Dict, List
from sqlalchemy import text
from app.db import engine


async def generate_program_for_active_stage(user_id: str) -> Dict:
    """
    MVP:
    - Берём активный stage пользователя (junior 1..3)
    - Находим level (1..3)
    - Для каждого модуля берём статьи с title LIKE '[J{level}]%'
    - Пишем в programma_polzovatelya как required
    """

    q_active_stage = text("""
        SELECT p.stage_id::text AS stage_id
        FROM progress_urovney_polzovatelya p
        WHERE p.user_id = CAST(:user_id AS uuid)
          AND p.status = 'active'
        LIMIT 1
    """)

    q_level = text("""
        SELECT level
        FROM urovni
        WHERE id = CAST(:stage_id AS uuid)
        LIMIT 1
    """)

    q_track = text("""
        SELECT track_id::text AS track_id
        FROM polzovateli
        WHERE id = CAST(:user_id AS uuid)
        LIMIT 1
    """)

    q_articles = text("""
        SELECT
          s.id::text AS article_id,
          s.module_id::text AS module_id
        FROM stati s
        JOIN moduli m ON m.id = s.module_id
        WHERE m.track_id = CAST(:track_id AS uuid)
          AND s.title LIKE :prefix
        ORDER BY s.title
    """)

    q_insert = text("""
        INSERT INTO programma_polzovatelya (user_id, stage_id, article_id, is_required)
        VALUES (CAST(:user_id AS uuid), CAST(:stage_id AS uuid), CAST(:article_id AS uuid), true)
        ON CONFLICT (user_id, stage_id, article_id) DO NOTHING
    """)

    async with engine.begin() as conn:
        r_stage = await conn.execute(q_active_stage, {"user_id": user_id})
        row_stage = r_stage.mappings().first()
        if not row_stage:
            return {"error": "active stage not found for user"}

        stage_id = row_stage["stage_id"]

        r_level = await conn.execute(q_level, {"stage_id": stage_id})
        row_level = r_level.first()
        if not row_level:
            return {"error": "stage not found"}
        level = int(row_level[0])

        r_track = await conn.execute(q_track, {"user_id": user_id})
        row_track = r_track.mappings().first()
        if not row_track:
            return {"error": "user not found"}
        track_id = row_track["track_id"]

        prefix = f"[J{level}]%"

        r_articles = await conn.execute(q_articles, {"track_id": track_id, "prefix": prefix})
        arts = r_articles.mappings().all()

        for a in arts:
            await conn.execute(q_insert, {
                "user_id": user_id,
                "stage_id": stage_id,
                "article_id": a["article_id"],
            })

    return {
        "user_id": user_id,
        "stage_id": stage_id,
        "level": level,
        "inserted_candidates": len(arts),
    }


async def get_program(user_id: str, stage_id: str | None = None) -> List[Dict]:
    q = text("""
        SELECT
          p.stage_id::text AS stage_id,
          p.article_id::text AS article_id,
          p.is_required,
          p.minitest_passed,
          p.minitest_passed_at,
          s.title,
          m.name AS module
        FROM programma_polzovatelya p
        JOIN stati s ON s.id = p.article_id
        JOIN moduli m ON m.id = s.module_id
        WHERE p.user_id = CAST(:user_id AS uuid)
          AND (:stage_id::uuid IS NULL OR p.stage_id = CAST(:stage_id AS uuid))
        ORDER BY m.name, s.title
    """)
    async with engine.connect() as conn:
        res = await conn.execute(q, {"user_id": user_id, "stage_id": stage_id})
        rows = res.mappings().all()
    return [dict(r) for r in rows]
