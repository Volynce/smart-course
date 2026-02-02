from typing import Dict, List
from sqlalchemy import text
from app.db import engine


async def submit_minitest(user_id: str, article_id: str, answers: List[Dict]) -> Dict:
    """
    answers: [{ "question_id": "...", "selected_option_id": "..." }, ...]
    Правило MVP: мини-тест считается пройденным только если ровно 3 ответа и все 3 правильные.
    """

    if len(answers) != 3:
        return {"passed": False, "correct": 0, "total": len(answers), "reason": "need exactly 3 answers"}

    # Проверяем правильность выбранных option_id
    q_check = text("""
        SELECT
          ao.id::text AS option_id,
          ao.question_id::text AS question_id,
          ao.is_correct
        FROM varianty_otveta ao
        WHERE ao.id = CAST(:option_id AS uuid)
        LIMIT 1
    """)

    correct = 0

    async with engine.begin() as conn:
        for a in answers:
            res = await conn.execute(q_check, {"option_id": a["selected_option_id"]})
            row = res.mappings().first()
            if row and row["is_correct"]:
                correct += 1

        passed = (correct == 3)

        # Обновляем факт прохождения мини-теста в программе пользователя
        q_update = text("""
            UPDATE programma_polzovatelya
            SET
              minitest_passed = :passed,
              minitest_passed_at = CASE WHEN :passed THEN now() ELSE NULL END
            WHERE user_id = CAST(:user_id AS uuid)
              AND article_id = CAST(:article_id AS uuid)
        """)
        await conn.execute(q_update, {"passed": passed, "user_id": user_id, "article_id": article_id})

    return {"passed": passed, "correct": correct, "total": 3}
