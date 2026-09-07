.PHONY: web api lint test db-up db-down migrate

web:
	npm run dev:web

api:
	python -m uvicorn dgn_picks_api.main:app --app-dir apps/api/src --reload --port 8000

lint:
	npm run lint:web

test:
	npm run test:api

db-up:
	docker compose up -d db

db-down:
	docker compose down

migrate:
	python -m alembic -c apps/api/alembic.ini upgrade head

