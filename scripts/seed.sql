-- 1) трек
INSERT INTO treki (name)
VALUES ('Разработчик')
ON CONFLICT (name) DO NOTHING;

-- 2) уровни (Junior 1..3)
INSERT INTO urovni (track_id, rank, level)
SELECT t.id, 'junior', v.level
FROM treki t
CROSS JOIN (VALUES (1),(2),(3)) AS v(level)
WHERE t.name = 'Разработчик'
ON CONFLICT (track_id, rank, level) DO NOTHING;

-- 3) 5 модулей
INSERT INTO moduli (track_id, name)
SELECT t.id, m.name
FROM treki t
CROSS JOIN (VALUES
  ('Frontend'),
  ('Backend'),
  ('Базы данных'),
  ('Внутренние стандарты'),
  ('HostCMS')
) AS m(name)
WHERE t.name = 'Разработчик'
ON CONFLICT (track_id, name) DO NOTHING;
