# Local Events App

Two-sided marketplace: venues post events, users discover nearby events.

## Stack

| Layer       | Choice                           |
|-------------|----------------------------------|
| Backend     | FastAPI (Python 3.14)            |
| Database    | PostgreSQL + PostGIS             |
| ORM         | SQLAlchemy / SQLModel + Alembic  |
| Auth        | JWT (access + refresh tokens)    |
| Frontend    | React Native                     |
| Deploy      | Docker (API + Postgres containers) |

## Repo layout

```
backend/       - FastAPI application
frontend/      - React Native app (empty, not yet scaffolded)
```

- Backend uses `pyproject.toml` for packaging (no `requirements.txt`).
- Python version pinned in `.python-version` (3.14). Keep in sync with Dockerfile.
- Dependencies are listed in `pyproject.toml`. Install via `uv sync`.

## First-time setup

```bash
cp .env.example .env               # edit SECRET_KEY
uv lock                             # generate uv.lock (commit it)
docker compose up -d               # starts API + Postgres
docker compose exec api alembic upgrade head   # create tables
```

## API endpoints (all built)

| Endpoint           | Auth required | Role required  |
|--------------------|---------------|----------------|
| POST /auth/register | No            | —              |
| POST /auth/login    | No            | —              |
| POST /auth/refresh  | No            | —              |
| GET /auth/me        | Yes           | —              |
| POST /venues        | Yes           | venue_owner    |
| GET /venues/{id}    | No            | —              |
| GET /venues         | No            | —              |
| POST /events        | Yes           | venue_owner    |
| GET /events/{id}    | No            | —              |
| GET /feed           | No            | —              |

## Remaining build order (frontend)

1. React Native auth screens
2. Feed screen
3. Event + venue creation screens

## Architecture decisions (from planning)

- **Geo queries**: Use PostGIS `ST_DWithin` from day one (not Python Haversine).
- **Auth**: Access token (15 min) + refresh token (30 days). Store in SecureStore (not AsyncStorage).
- **Roles**: Simple `role` flag on users table (`user` / `venue_owner`). No complex permissions.
- **No Redis for MVP**: PostgreSQL alone is sufficient. Add Redis later for caching, background jobs, or rate limiting.
- **Events always belong to a venue** – no standalone events.
- **Feed**: radius filter (1/5/20 km), sorted by `start_time` ascending. No ranking AI.
- **Map view** is Phase 2 if time permits.

## MVP scope cuts (don't build)

Payments, ticketing, chat, social graph, followers, recommendations, push notifications, reviews, event approval workflow.

## Database models (minimal)

- `users(id, email, password_hash, role)`
- `venues(id, owner_id, name, lat, lng, address)`
- `events(id, venue_id, title, description, start_time, end_time, tags, image_url?)`
