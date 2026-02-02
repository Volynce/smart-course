-- Назначаем пользователю 1 статью на stage Junior 1 как required
-- user_id и stage_id подставлены под твоего test2-пользователя

INSERT INTO programma_polzovatelya (user_id, stage_id, article_id, is_required, created_at, minitest_passed, minitest_passed_at)
SELECT
  '2ffa9328-78b0-45b3-a8ea-eb861bcd1a70'::uuid AS user_id,
  'ddbf9c14-62ea-4a33-82d7-1c50819db39d'::uuid AS stage_id,
  s.id AS article_id,
  true AS is_required,
  now() AS created_at,
  NULL AS minitest_passed,
  NULL AS minitest_passed_at
FROM stati s
WHERE s.title = 'Введение в Smart Course'
ON CONFLICT (user_id, stage_id, article_id) DO NOTHING;
