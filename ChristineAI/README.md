# ChristineAI Backend

Репозиторий приведён к единому сервисному формату: FastAPI backend для speech roleplay-платформы с мульти-провайдерным LLM router, админкой и MCP-совместимыми API.

## Что входит

- `app/` — FastAPI приложение
- `app/api/v1` — auth, assistants, devices, chat, mcp-tools, admin
- `app/providers/llm.py` — multi-provider router (`mock`, `openai`, `openrouter`, `anthropic`, `ollama`) + fallback
- `app/services/observability.py` — runtime метрики и журнал turn-ов
- `docker-compose.yml` — `api + db + redis`
- `scripts/smoke_phase1.py` — end-to-end smoke test
- `tests/` — unit + integration

## Удалено в рамках рефакторинга

Удалены legacy-компоненты старой монолитной версии (старый `christine/*`, `christine-server`, `christine_head`, `httpserver`, `tools`, старые systemd-юниты и сопутствующие артефакты), не используемые текущим backend-контуром.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build -d
```

Проверка:

```bash
curl http://localhost:8000/health
python3 scripts/smoke_phase1.py
```

## Точки входа

- OpenAPI: `http://localhost:8000/docs`
- MCP endpoint: `http://localhost:8000/mcp`
- Admin console: `http://localhost:8000/admin`

### Global admin режим

Чтобы в веб-админке управлять всеми пользователями (users/assistants/devices), задайте в `.env`:

```bash
CHRISTINE_ADMIN_API_KEY=your-strong-admin-key
```

После логина введите этот ключ в поле `X-Admin-Key` в верхней панели `/admin`.

## Тесты и линт

```bash
./.venv/bin/ruff check app tests
./.venv/bin/pytest -q
```
