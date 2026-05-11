.PHONY: dev api frontend db-up db-down migrate seed test lint typecheck

dev:
	docker compose up --build

api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

db-up:
	docker compose up -d postgres redis

db-down:
	docker compose down

migrate:
	alembic upgrade head

seed:
	python -m scraper.seed_demo_data

test:
	pytest

lint:
	ruff check .

typecheck:
	pyright
