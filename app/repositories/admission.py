from typing import Dict
from sqlalchemy import text
from app.db import engine


async def stage_admission(user_id: str) -> Dict:
    """
    Возвращает:
    - active_stage_id
    - required_total
    - required_passed
    - can_take_stage_diagnostic (true если required_total == required_passed)
    """

    # 1) Найти активный stage пользователя
    q_stage = text("""
        SELECT stage_id::text AS stage_id
        FROM progress_urovney_polzovatelya
        WHERE user_id = CAST(:user_id AS uuid)
          AND status = 'active'
        LIMIT 1
    """)

    # 2) Посчитать required и required_passed на этом stage
    q_counts = text("""
        SELECT
          COUNT(*) FILTER (WHERE is_required = true) AS required_total,
          COUNT(*) FILTER (WHERE is_required = true AND minitest_passed = true) AS required_passed
        FROM programma_polzovatelya
        WHERE user_id = CAST(:user_id AS uuid)
          AND stage_id = CAST(:stage_id AS uuid)
    """)

    async with engine.connect() as conn:
        sres = await conn.execute(q_stage, {"user_id": user_id})
        stage = sres.mappings().first()
        if not stage:
            return {
                "active_stage_id": None,
                "required_total": 0,
                "required_passed": 0,
                "can_take_stage_diagnostic": False,
                "reason": "no active stage",
            }

        cres = await conn.execute(q_counts, {"user_id": user_id, "stage_id": stage["stage_id"]})
        c = cres.mappings().first() or {"required_total": 0, "required_passed": 0}

    required_total = int(c["required_total"] or 0)
    required_passed = int(c["required_passed"] or 0)

    return {
        "active_stage_id": stage["stage_id"],
        "required_total": required_total,
        "required_passed": required_passed,
        "can_take_stage_diagnostic": (required_total == required_passed and required_total > 0),
    }
