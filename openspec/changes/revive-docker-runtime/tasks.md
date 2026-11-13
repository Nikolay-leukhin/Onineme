# Tasks

## 1. Зависимости

- [x] 1.1 В `requirements.txt` удалить `bson`, `win32-setctime`, `pip`, `setuptools`, `wheel`, заменить `psycopg2` на `psycopg2-binary==2.9.6`; проверить: `docker run --rm -v "$PWD":/app -w /app python:3.11-slim pip install -r requirements.txt` завершается успешно, и `python -c "from bson import ObjectId; import pymongo, psycopg2, aiogram"` в том же контейнере не падает

## 2. Схема БД

- [ ] 2.1 В `main.py` после создания `DataBase` вызвать `database.schema_manager.create_all_schemas()`; проверить при задаче 5.2: в логах бота есть «database creation started», в PostgreSQL появились таблицы `users`, `titles`, `users_titles`, а повторный запуск сохраняет записи

## 3. Устойчивость фоновых циклов и запросов

- [ ] 3.1 В `external_services/api_service.py` выполнять `requests.get` через `asyncio.to_thread` с `timeout=30`; в `get_all_html_pages` прерывать обход на коде ответа ≠ 200 и после 50 страниц; проверить: код содержит таймаут и лимит, и при задаче 5.3 бот отвечает на /help во время синхронизации
- [ ] 3.2 В `CollectionManager.start_updating_collection_loop` обернуть итерацию в `try/except Exception` с `logger.exception`; после ошибки ждать 1 час, после успеха — 24 часа; `CancelledError` не перехватывать; проверить при задаче 5.3: ошибка парсинга в логах и процесс продолжает работу
- [ ] 3.3 В `UpdateController.start_mailing_update_loop` обернуть итерацию в `try/except Exception` с `logger.exception`, сохранив интервал 180 с; проверить при задаче 5.3: после ошибки через ~3 минуты в логах видна следующая попытка

## 4. Контейнеризация

- [x] 4.1 Добавить `.dockerignore` (исключить `.env`, `.git`, `.idea`, `.claude`, `openspec`, `__pycache__`); проверить: `docker run --rm --entrypoint ls <образ> -a /app` не показывает `.env`
- [x] 4.2 Добавить `Dockerfile` на `python:3.11-slim`: установка `requirements.txt`, копирование кода, `PYTHONUNBUFFERED=1`, `CMD ["python", "main.py"]`; проверить: `docker compose build bot` проходит без ошибок
- [x] 4.3 Добавить `docker-compose.yml` с сервисами `postgres` (16-alpine, healthcheck `pg_isready`, том `pg_data`), `mongo` (7, healthcheck `mongosh ping`, том `mongo_data`) и `bot` (`build: .`, `env_file: .env`, переменные `DB_*`/`MONGO_*` с дефолтами, `depends_on: service_healthy`, `restart: unless-stopped`; `restart: unless-stopped` и у хранилищ); проверить: `docker compose config` проходит без ошибок
- [x] 4.4 Добавить `.env.example` со всеми переменными (`TELEGRAM_TOKEN` пустой, остальные — значения по умолчанию из compose); проверить: `git check-ignore .env` возвращает `.env`, а `.env.example` отслеживается
- [x] 4.5 Переписать `README.md` в UTF-8: назначение, требования (Docker + Compose v2), шаги запуска, просмотр логов, остановка и сброс данных; проверить: `file README.md` показывает UTF-8, и шаги из README выполняются как написано при задаче 5.1

## 5. Интеграционная проверка

- [ ] 5.1 Выполнить `docker compose up -d --build` с `.env`, содержащим `TELEGRAM_TOKEN`; проверить: `docker compose ps` показывает `bot` running, `postgres` и `mongo` healthy, и бот не перезапускается в цикле в течение 5 минут
- [ ] 5.2 Отправить боту /start в Telegram; проверить: бот отвечает приветствием, в таблице `users` появилась запись; после `docker compose down` и `docker compose up -d` запись сохранилась
- [ ] 5.3 Проверить по `docker compose logs bot`, что ошибки парсера (если есть) логируются без завершения процесса, и что во время синхронизации каталога бот отвечает на /help; если polling падает из-за несовместимости `aiogram==3.0.0b6` с текущим Bot API — поднять aiogram до минимальной совместимой версии 3.x, зафиксировать это в design.md и повторить 5.1–5.2

## Workflow follow-up

- Архивировать изменение после проверки запуска (`/opsx:archive`).
- Отдельным изменением: починка парсера AnimeGo и обновление стека.
