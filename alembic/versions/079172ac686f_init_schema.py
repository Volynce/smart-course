"""init schema

Revision ID: 079172ac686f
Revises: 
Create Date: 2026-02-02 23:46:51.103470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '079172ac686f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # UUID генератор
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.execute("""
    CREATE TABLE treki (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      name text NOT NULL UNIQUE
    );
    """)

    op.execute("""
    CREATE TABLE urovni (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      track_id uuid NOT NULL REFERENCES treki(id) ON DELETE RESTRICT,
      rank text NOT NULL CHECK (rank IN ('junior','specialist','senior')),
      level smallint NOT NULL CHECK (level BETWEEN 1 AND 3),
      UNIQUE (track_id, rank, level)
    );
    """)

    op.execute("""
    CREATE TABLE moduli (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      track_id uuid NOT NULL REFERENCES treki(id) ON DELETE RESTRICT,
      name text NOT NULL,
      UNIQUE (track_id, name)
    );
    """)

    op.execute("""
    CREATE TABLE polzovateli (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      email text NOT NULL UNIQUE,
      full_name text NOT NULL,
      department text,
      position_title text,
      track_id uuid NOT NULL REFERENCES treki(id) ON DELETE RESTRICT,
      created_at timestamptz NOT NULL DEFAULT now()
    );
    """)

    op.execute("""
    CREATE TABLE stati (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      module_id uuid NOT NULL REFERENCES moduli(id) ON DELETE RESTRICT,
      title text NOT NULL,
      content text NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE programma_polzovatelya (
      user_id uuid NOT NULL REFERENCES polzovateli(id) ON DELETE CASCADE,
      stage_id uuid NOT NULL REFERENCES urovni(id) ON DELETE RESTRICT,
      article_id uuid NOT NULL REFERENCES stati(id) ON DELETE CASCADE,
      is_required boolean NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(),
      minitest_passed boolean,
      minitest_passed_at timestamptz,
      PRIMARY KEY (user_id, stage_id, article_id),
      CHECK (
        (minitest_passed IS NULL AND minitest_passed_at IS NULL)
        OR
        (minitest_passed = true AND minitest_passed_at IS NOT NULL)
        OR
        (minitest_passed = false AND minitest_passed_at IS NULL)
      )
    );
    """)

    op.execute("""
    CREATE TABLE progress_neobyaz_statey (
      user_id uuid NOT NULL REFERENCES polzovateli(id) ON DELETE CASCADE,
      article_id uuid NOT NULL REFERENCES stati(id) ON DELETE CASCADE,
      is_read boolean NOT NULL DEFAULT false,
      read_at timestamptz,
      PRIMARY KEY (user_id, article_id),
      CHECK (
        (is_read = false AND read_at IS NULL)
        OR
        (is_read = true AND read_at IS NOT NULL)
      )
    );
    """)

    op.execute("""
    CREATE TABLE progress_urovney_polzovatelya (
      user_id uuid NOT NULL REFERENCES polzovateli(id) ON DELETE CASCADE,
      stage_id uuid NOT NULL REFERENCES urovni(id) ON DELETE RESTRICT,
      status text NOT NULL CHECK (status IN ('active','completed')),
      activated_at timestamptz NOT NULL DEFAULT now(),
      completed_at timestamptz,
      PRIMARY KEY (user_id, stage_id),
      CHECK (
        (status = 'active' AND completed_at IS NULL)
        OR
        (status = 'completed' AND completed_at IS NOT NULL)
      )
    );
    """)

    op.execute("""
    CREATE TABLE voprosy (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      module_id uuid NOT NULL REFERENCES moduli(id) ON DELETE RESTRICT,
      rank text NOT NULL CHECK (rank IN ('junior','specialist','senior')),
      stage_level smallint NOT NULL CHECK (stage_level BETWEEN 1 AND 3),
      text text NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE varianty_otveta (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      question_id uuid NOT NULL REFERENCES voprosy(id) ON DELETE CASCADE,
      text text NOT NULL,
      is_correct boolean NOT NULL DEFAULT false
    );
    """)

    op.execute("""
    CREATE TABLE minitest_voprosy (
      article_id uuid NOT NULL REFERENCES stati(id) ON DELETE CASCADE,
      pos smallint NOT NULL CHECK (pos BETWEEN 1 AND 3),
      question_id uuid NOT NULL REFERENCES voprosy(id) ON DELETE RESTRICT,
      PRIMARY KEY (article_id, pos),
      UNIQUE (article_id, question_id)
    );
    """)

    op.execute("""
    CREATE TABLE diagnostiki (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id uuid NOT NULL REFERENCES polzovateli(id) ON DELETE CASCADE,
      type text NOT NULL CHECK (type IN ('entry','stage')),
      stage_id uuid REFERENCES urovni(id) ON DELETE RESTRICT,
      created_at timestamptz NOT NULL DEFAULT now(),
      total_q smallint NOT NULL DEFAULT 10 CHECK (total_q = 10),
      score_total smallint NOT NULL CHECK (score_total BETWEEN 0 AND total_q),
      CHECK (
        (type = 'entry' AND stage_id IS NULL)
        OR
        (type = 'stage' AND stage_id IS NOT NULL)
      )
    );
    """)

    op.execute("""
    CREATE UNIQUE INDEX ux_diagnostiki_entry_once
    ON diagnostiki(user_id)
    WHERE type = 'entry';
    """)

    op.execute("""
    CREATE UNIQUE INDEX ux_diagnostiki_stage_once
    ON diagnostiki(user_id, stage_id)
    WHERE type = 'stage';
    """)

    op.execute("""
    CREATE TABLE diagnostika_stats (
      diagnostika_id uuid NOT NULL REFERENCES diagnostiki(id) ON DELETE CASCADE,
      module_id uuid NOT NULL REFERENCES moduli(id) ON DELETE RESTRICT,
      correct_cnt smallint NOT NULL CHECK (correct_cnt >= 0),
      total_cnt smallint NOT NULL CHECK (total_cnt >= 0),
      PRIMARY KEY (diagnostika_id, module_id),
      CHECK (correct_cnt <= total_cnt)
    );
    """)

    op.execute("""
    CREATE TABLE itogovye_popytki (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id uuid NOT NULL REFERENCES polzovateli(id) ON DELETE CASCADE,
      rank text NOT NULL CHECK (rank IN ('junior','specialist','senior')),
      attempt_no int NOT NULL CHECK (attempt_no >= 1),
      based_on_attempt_id uuid REFERENCES itogovye_popytki(id) ON DELETE SET NULL,
      created_at timestamptz NOT NULL DEFAULT now(),
      submitted_at timestamptz,
      total_q smallint NOT NULL DEFAULT 20 CHECK (total_q = 20),
      score_total smallint CHECK (score_total BETWEEN 0 AND total_q),
      passed boolean,
      UNIQUE (user_id, rank, attempt_no),
      CHECK (
        (submitted_at IS NULL AND score_total IS NULL AND passed IS NULL)
        OR
        (submitted_at IS NOT NULL AND score_total IS NOT NULL AND passed IS NOT NULL)
      )
    );
    """)

    op.execute("""
    CREATE TABLE voprosy_v_itogovoy_popytke (
      final_attempt_id uuid NOT NULL REFERENCES itogovye_popytki(id) ON DELETE CASCADE,
      question_id uuid NOT NULL REFERENCES voprosy(id) ON DELETE RESTRICT,
      module_id uuid NOT NULL REFERENCES moduli(id) ON DELETE RESTRICT,
      PRIMARY KEY (final_attempt_id, question_id)
    );
    """)

    op.execute("""
    CREATE TABLE otvety_v_itogovoy_popytke (
      final_attempt_id uuid NOT NULL REFERENCES itogovye_popytki(id) ON DELETE CASCADE,
      question_id uuid NOT NULL REFERENCES voprosy(id) ON DELETE RESTRICT,
      selected_option_id uuid NOT NULL REFERENCES varianty_otveta(id) ON DELETE RESTRICT,
      is_correct boolean NOT NULL,
      PRIMARY KEY (final_attempt_id, question_id)
    );
    """)

    # Индексы
    op.execute("CREATE INDEX ix_stati_module ON stati(module_id);")
    op.execute("CREATE INDEX ix_voprosy_scope ON voprosy(rank, stage_level, module_id);")
    op.execute("CREATE INDEX ix_prog_user_stage ON programma_polzovatelya(user_id, stage_id);")


def downgrade() -> None:
    # откат в обратном порядке
    op.execute("DROP INDEX IF EXISTS ix_prog_user_stage;")
    op.execute("DROP INDEX IF EXISTS ix_voprosy_scope;")
    op.execute("DROP INDEX IF EXISTS ix_stati_module;")

    op.execute("DROP TABLE IF EXISTS otvety_v_itogovoy_popytke;")
    op.execute("DROP TABLE IF EXISTS voprosy_v_itogovoy_popytke;")
    op.execute("DROP TABLE IF EXISTS itogovye_popytki;")
    op.execute("DROP TABLE IF EXISTS diagnostika_stats;")
    op.execute("DROP INDEX IF EXISTS ux_diagnostiki_stage_once;")
    op.execute("DROP INDEX IF EXISTS ux_diagnostiki_entry_once;")
    op.execute("DROP TABLE IF EXISTS diagnostiki;")
    op.execute("DROP TABLE IF EXISTS minitest_voprosy;")
    op.execute("DROP TABLE IF EXISTS varianty_otveta;")
    op.execute("DROP TABLE IF EXISTS voprosy;")
    op.execute("DROP TABLE IF EXISTS progress_urovney_polzovatelya;")
    op.execute("DROP TABLE IF EXISTS progress_neobyaz_statey;")
    op.execute("DROP TABLE IF EXISTS programma_polzovatelya;")
    op.execute("DROP TABLE IF EXISTS stati;")
    op.execute("DROP TABLE IF EXISTS polzovateli;")
    op.execute("DROP TABLE IF EXISTS moduli;")
    op.execute("DROP TABLE IF EXISTS urovni;")
    op.execute("DROP TABLE IF EXISTS treki;")

    # расширение можно не удалять