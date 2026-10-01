# Smart Task Tracker — Архітектура проєкту (Модуль 1)

## Структура файлів

```
task-tracker/
├── pyproject.toml
├── uv.lock
├── .env                          # секрети (SECRET_KEY, DB_URL) — у .gitignore!
├── .env.example                  # приклад без реальних значень — у Git
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/                 # згенеровані міграції
└── src/
    └── task_tracker/
        ├── __init__.py
        ├── main.py                # створення FastAPI app, підключення роутерів
        ├── config.py              # pydantic-settings, читає .env
        ├── database.py            # engine, async_sessionmaker, get_db_session
        │
        ├── models/                # SQLAlchemy ORM-моделі
        │   ├── __init__.py
        │   ├── base.py            # DeclarativeBase
        │   ├── user.py            # UserORM
        │   └── task.py            # TaskORM
        │
        ├── schemas/                # Pydantic-моделі (DTO)
        │   ├── __init__.py
        │   ├── user.py            # UserCreate, UserResponse
        │   └── task.py            # TaskCreate, TaskResponse, TaskUpdate
        │
        ├── auth/
        │   ├── __init__.py
        │   ├── security.py        # hash_password, verify_password, create tokens
        │   └── dependencies.py    # get_current_user
        │
        ├── crud/                   # функції роботи з БД
        │   ├── __init__.py
        │   ├── user.py
        │   └── task.py
        │
        ├── routers/                 # ендпоінти
        │   ├── __init__.py
        │   ├── auth.py             # /auth/register, /auth/login, /auth/refresh
        │   └── tasks.py            # /tasks CRUD + /tasks/{id}/summarize
        │
        └── services/
            ├── __init__.py
            └── ai_client.py        # AIMockClient переїжджає сюди
```

## Логіка поділу (layered architecture)

Той самий принцип, що в Spring (`controller` → `service` → `repository`), з іншими назвами:

| Шар | Назва тут | Аналог у Spring |
|---|---|---|
| Вхідна точка, HTTP | `routers/` | `@RestController` |
| Бізнес-логіка | `services/` | `@Service` |
| Доступ до БД | `crud/` | `@Repository` |
| Структура таблиць | `models/` | JPA `@Entity` |
| Контракт API (DTO) | `schemas/` | DTO-класи |
| Авторизація | `auth/` | Spring Security |

### `models/` vs `schemas/`

Різниця `TaskORM` (БД) vs `TaskModel`/`TaskResponse` (API-контракт). Розділені в окремі папки, бо в реальному проєкті моделей БД і схем API стає багато.

### `config.py` через pydantic-settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

Якщо `.env` не містить `database_url`, Pydantic одразу кине `ValidationError` при старті застосунку — проблема конфігурації виявляється одразу, а не в середині роботи.

## Порядок написання (знизу вгору по залежностях)

1. **`config.py` + `.env`** — налаштування проєкту
2. **`database.py` + `models/`** — підключення до БД, опис таблиць, перша Alembic-міграція
3. **`schemas/`** — Pydantic DTO для User і Task
4. **`auth/`** — хешування паролів, JWT, `get_current_user`
5. **`crud/`** — функції запитів до БД (реєстрація, CRUD задач)
6. **`services/ai_client.py`** — перенесення `AIMockClient`
7. **`routers/`** — ендпоінти, що зв'язують усе разом
8. **`Dockerfile` + `docker-compose.yml`** — контейнеризація

## Функціонал проєкту (з початкового плану)

1. **Реєстрація та Авторизація**: JWT-токени (Access + Refresh), хешування паролів через passlib/bcrypt
2. **CRUD для задач/проєктів**: створення, читання, оновлення, видалення з фільтрацією та пагінацією
3. **Асинхронний мокінг AI-сервісу**: `/tasks/{id}/summarize`, що асинхронно симулює звернення до AI (затримка 2–3 сек через `asyncio.sleep`) і повертає резюме задачі
4. **Контейнеризація**: запуск однією командою `docker compose up --build`

## JWT та хешування паролів — ключові відмінності від Java/Spring

Концепції ідентичні (RFC 7519, bcrypt), відрізняються лише бібліотеки:

**Хешування паролів:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd_context.hash("my_password")
pwd_context.verify("my_password", hashed)  # True/False
```

**JWT:**
```python
from jose import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**Специфічний для FastAPI патерн — `OAuth2PasswordBearer` + `Depends`:**
```python
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> UserORM:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = await session.get(UserORM, user_id)
    if user is None:
        raise HTTPException(401, "User not found")
    return user
```

`OAuth2PasswordBearer` сам знає, як витягти токен із заголовка `Authorization`, і Swagger UI сам показує кнопку "Authorize" на основі цього.
