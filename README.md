# Smart Course (MVP)

## Цель
Информационная система для подготовки и прохождения обучающих курсов
по индивидуальной траектории обучения.

## Быстрый старт (dev)
1) Создать и активировать виртуальное окружение
2) Установить зависимости
3) Запустить API
4) Проверить `/health`

## Конфигурация
Настройки задаются через переменные окружения.
Пример: `.env.example` (реальный `.env` не коммитится)

## Журнал изменений
### 2026-02-02
- Созданы базовые файлы проекта (README, .gitignore) и папка app/
## База данных (PostgreSQL)
В dev-режиме используем PostgreSQL в Docker.

Запуск:
docker run --name smart-course-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=smart_course -p 5432:5432 -d postgres:16

Проверка:
docker exec -it smart-course-postgres psql -U postgres -d smart_course -c "SELECT 1;"

## Быстрый старт (PostgreSQL + миграции + seed)

### 1) Запуск PostgreSQL в Docker
Контейнер: `smart-course-postgres`  
База: `smart_course`

```bash
docker run --name smart-course-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=smart_course -p 5432:5432 -d postgres:16
Проверка:

docker exec -it smart-course-postgres psql -U postgres -d smart_course -c "SELECT 1;"
2) Применить миграции
alembic upgrade head
3) Заполнить минимальные данные (seed)
docker exec -i smart-course-postgres psql -U postgres -d smart_course < scripts/seed.sql
4) Запуск API
uvicorn app.main:app --reload
Проверки:

http://127.0.0.1:8000/health

http://127.0.0.1:8000/db-ping