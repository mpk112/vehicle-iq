.PHONY: help up down logs test lint format migrate seed

help:
	@echo "VehicleIQ Development Commands"
	@echo "=============================="
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make logs        - View logs"
	@echo "make test        - Run tests"
	@echo "make lint        - Run linters"
	@echo "make format      - Format code"
	@echo "make migrate     - Run database migrations"
	@echo "make seed        - Seed database with test data"

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	cd backend && pytest --cov=app --cov-report=html
	cd frontend && npm test -- --coverage

lint:
	cd backend && ruff check app/
	cd frontend && npm run lint

format:
	cd backend && black app/ && ruff check --fix app/
	cd frontend && npm run format

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python scripts/seed.py
