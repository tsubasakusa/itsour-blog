# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Itsour Blog is a full-stack content management system (blog + portfolio) with a newspaper-style yellow/black UI theme. The project is in Traditional Chinese (zh-TW).

## Architecture

- **Backend**: FastAPI (Python) at `backend/app/`
  - SQLAlchemy ORM with PostgreSQL
  - Elasticsearch for full-text search (`search.py`)
  - JWT auth with single admin user (hardcoded credentials via env vars, `auth.py`)
  - File uploads stored in `backend/uploads/`
  - API routes prefixed `/api/articles/` and `/api/auth/`
- **Frontend**: Vue 3 (Options API with `setup()`) + Vite at `frontend/`
  - No vue-router routing — uses a `view` ref in `App.vue` to switch between home/login/admin views
  - Pinia is installed but state is managed locally in components
  - Axios client in `src/api.js` with JWT interceptor (token in localStorage)
  - Components: FrontPage (public), AdminPanel (CRUD), ArticleModal, LoginPage, GrainOverlay
- **Infrastructure**: `docker-compose.yml` runs PostgreSQL 15 and Elasticsearch 8.11 (no app containers)

## Common Commands

### Start infrastructure
```bash
docker-compose up -d   # PostgreSQL on :5432, Elasticsearch on :9200
```

### Backend development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload   # Runs on :8000
```

### Frontend development
```bash
cd frontend
npm install
npm run dev    # Runs on :5173
npm run build  # Production build
```

### Run backend tests
```bash
cd backend
pytest                    # All tests
pytest tests/test_api.py  # API tests
```

### API docs
FastAPI auto-generates docs at `http://localhost:8000/docs`

## Key Data Models (`backend/app/models.py`)

- **Article**: title, content, summary, author, category, is_published, view_count, featured
- **Image**: filename, filepath, alt_text, linked to Article
- **Tag**: name, color — many-to-many with Article via `article_tags` join table

## Environment Variables

- `DATABASE_URL` (default: `postgresql://blog_user:blog_password@localhost:5432/blog_db`)
- `ELASTICSEARCH_URL` (default: `http://localhost:9200`)
- `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` (defaults: `your-secret-key-change-this`, `admin`, `admin123`)

## Notes

- Elasticsearch operations are fire-and-forget (errors are printed, not raised) — the app works without ES running, but search will return empty results
- Database tables are auto-created via `Base.metadata.create_all()` in `main.py` (no Alembic migrations are actively used despite being in requirements)
- CORS is configured for `http://localhost:5173` only
