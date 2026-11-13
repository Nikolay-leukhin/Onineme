# Design

## Context

Мотивация — см. proposal.md («Why»). Текущее состояние, важное для решений:

- Один процесс `main.py` (aiogram 3.0.0b6) запускает через `asyncio.gather` три задачи: polling, `CollectionManager.start_updating_collection_loop` и `UpdateController.start_mailing_update_loop`. Ни один цикл не перехватывает исключения, поэтому сбой парсера завершает `gather` и весь процесс.
- `ApiService` использует синхронный `requests.get` без таймаута внутри корутин — это блокирует event loop. `get_all_html_pages` крутится, пока на странице не встретится маркер 404; если сайт отдаёт, например, страницу защиты от ботов, цикл бесконечен.
- `config_data/config.py` читает `TELEGRAM_TOKEN` (он задан в `.env`), `DB_*` и `MONGO_*`; последних в `.env` нет.
- Модели SQLAlchemy (`data/models/models.py`) и `DatabaseSchemaManager.create_all_schemas()` существуют, но при запуске не вызываются.
- `requirements.txt` — заморозка Windows-окружения: `win32-setctime`, `pip`/`setuptools`/`wheel`, отдельный пакет `bson` (перекрывает модуль `bson` из `pymongo` и ломает `from bson import ObjectId`), `psycopg2` (требует компиляции).
- `README.md` в UTF-16.

## Goals / Non-Goals

**Goals:**
- `docker compose up -d --build` поднимает бот, PostgreSQL и MongoDB; бот отвечает на /start.
- Процесс бота переживает любые сбои парсинга AnimeGo.

**Non-Goals:**
- Починка селекторов парсера, обновление aiogram/pydantic/SQLAlchemy до актуальных версий, миграции схемы (Alembic), тесты для бизнес-логики — всё это войдёт в последующую переработку.

## Decisions

1. **Базовый образ `python:3.11-slim`.** README указывает Python 3.11; закреплённые `aiohttp==3.8.4` и `aiogram==3.0.0b6` не имеют колёс для 3.12+. Альтернатива — обновлять зависимости — откладывается до переработки, чтобы сейчас не чинить API-несовместимости.

2. **Минимальная правка `requirements.txt`.** Удалить `bson`, `win32-setctime`, `pip`, `setuptools`, `wheel`; заменить `psycopg2` на `psycopg2-binary==2.9.6`; остальные пины оставить. Альтернатива (полный апгрейд) — вне целей.

3. **Compose: три сервиса + именованные тома.**
   - `postgres:16-alpine` с `pg_isready` в healthcheck, том `pg_data`.
   - `mongo:7` с `mongosh --eval "db.adminCommand('ping')"` в healthcheck, том `mongo_data`.
   - `bot`: `build: .`, `env_file: .env`, `depends_on` с `condition: service_healthy`, `restart: unless-stopped`.
   - Параметры подключения (`DB_HOST=postgres`, `DB_PORT=5432`, `MONGO_URL=mongodb://mongo:27017`, имена БД, пользователь/пароль) задаются в `environment` compose со значениями по умолчанию через `${VAR:-default}`, чтобы для запуска хватало одного `TELEGRAM_TOKEN` в `.env`. Те же переменные пароля передаются в контейнер PostgreSQL. Порты хранилищ наружу не публикуются.

4. **Схема создаётся при старте через `Base.metadata.create_all`.** Метод уже есть (`DatabaseSchemaManager.create_all_schemas`), `create_all` идемпотентен (создаёт только отсутствующие таблицы). Альтернатива — SQL-скрипт в `docker-entrypoint-initdb.d` — дублирует модели и выполняется только на пустом томе. Вызов `drop_all_schemas` не используется.

5. **Защитная обёртка фоновых циклов.** Тело каждой итерации в `CollectionManager` и `UpdateController` оборачивается в `try/except Exception` с `logger.exception`; после ошибки цикл спит и повторяет. Для синхронизации каталога после ошибки используется более короткая пауза (1 час) вместо 24 часов, чтобы не ждать сутки после временного сбоя. `asyncio.CancelledError` не перехватывается.

6. **Неблокирующие запросы с таймаутом и лимитом страниц.** В `ApiService` вызовы `requests.get` выполняются через `asyncio.to_thread(..., timeout=30)`; в `get_all_html_pages` добавляется лимит (50 страниц) и остановка на ответе с кодом ≠ 200. Альтернатива — переход на `aiohttp` — меняет больше кода; оставлено для переработки.

7. **Имя требования «Схема БД существует заранее» сохраняется** в дельте bot-runtime (MODIFIED требует точного заголовка); переименование можно сделать отдельно.


## Risks / Trade-offs

- [Парсер AnimeGo, скорее всего, не работает (домен/разметка/антибот)] → циклы логируют ошибку и не роняют бота; функции каталога и уведомлений будут пустыми до переработки парсера.
- [`aiogram==3.0.0b6` — бета, может не совместиться с текущим Bot API] → при запуске проверяем /start вручную; если polling падает на разборе ответов Telegram, фиксируем минимальный апгрейд в рамках задачи 3 и отражаем в tasks.
- [`create_all` не применяет изменения к уже существующим таблицам] → приемлемо, пока нет миграций; схема меняется только в будущей переработке.
- [Пароль PostgreSQL по умолчанию в compose] → порты БД не публикуются наружу; значения можно переопределить в `.env`.
- [Бот при каждом старте вызывает `set_my_commands` и `delete_webhook`] → при неверном токене процесс падает и перезапускается в цикле; видно по `docker compose logs bot`.

## Migration Plan

1. Скопировать `.env.example` → `.env`, заполнить `TELEGRAM_TOKEN`.
2. `docker compose up -d --build`; проверить `docker compose ps` и `docker compose logs -f bot`.
3. Откат: `docker compose down` (данные остаются в томах); полный сброс — `docker compose down -v`.
