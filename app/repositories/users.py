from typing import Dict
from sqlalchemy import text
from app.db import engine


async def create_user(
    email: str,
    full_name: str,
    track_id: str,
    department: str | None = None,
    position_title: str | None = None,
) -> Dict:
    # 1) Находим stage junior level=1 для данного track_id
    q_stage = text("""
        SELECT id::text AS id
        FROM urovni
        WHERE track_id = :track_id
          AND rank = 'junior'
          AND level = 1
        LIMIT 1
    """)

    # 2) Создаём пользователя
    q_user = text("""
        INSERT INTO polzovateli (email, full_name, department, position_title, track_id)
        VALUES (:email, :full_name, :department, :position_title, :track_id)
        RETURNING
          id::text AS id,
          email,
          full_name,
          department,
          position_title,
          track_id::text AS track_id
    """)

    # 3) Активируем stage (progress_urovney_polzovatelya)
    # ВАЖНО: каст делаем через CAST(:param AS uuid), а не :param::uuid
    q_progress = text("""
        INSERT INTO progress_urovney_polzovatelya (user_id, stage_id, status, activated_at)
        VALUES (CAST(:user_id AS uuid), CAST(:stage_id AS uuid), 'active', now())
        ON CONFLICT (user_id, stage_id) DO NOTHING
    """)

    async with engine.begin() as conn:
        stage_res = await conn.execute(q_stage, {"track_id": track_id})
        stage = stage_res.mappings().first()
        if not stage:
            raise ValueError("junior level=1 stage not found for this track_id")

        user_res = await conn.execute(
            q_user,
            {
                "email": email,
                "full_name": full_name,
                "department": department,
                "position_title": position_title,
                "track_id": track_id,
            },
        )
        user = user_res.mappings().first()
        if not user:
            raise ValueError("failed to create user")

        await conn.execute(q_progress, {"user_id": user["id"], "stage_id": stage["id"]})

    return dict(user) | {"active_stage_id": stage["id"]}


async def get_user(user_id: str) -> Dict:
    q = text("""
        SELECT
          u.id::text AS id,
          u.email,
          u.full_name,
          u.department,
          u.position_title,
          u.track_id::text AS track_id,
          p.stage_id::text AS active_stage_id
        FROM polzovateli u
        LEFT JOIN progress_urovney_polzovatelya p
          ON p.user_id = u.id
         AND p.status = 'active'
        WHERE u.id = CAST(:user_id AS uuid)
        LIMIT 1
    """)

    async with engine.connect() as conn:
        res = await conn.execute(q, {"user_id": user_id})
        row = res.mappings().first()

    if not row:
        raise ValueError("user not found")

    return dict(row)
