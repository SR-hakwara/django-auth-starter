.PHONY: help install makemigrations migrate run test coverage lint format check superuser messages

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

makemigrations: ## Generate new migration files (dev only — do not run in CI)
	python manage.py makemigrations

migrate: ## Apply existing migrations
	python manage.py migrate

run: ## Start development server
	python manage.py runserver

test: ## Run tests with pytest
	pytest -v

coverage: ## Run tests with coverage report
	pytest --cov=apps --cov-report=term-missing

lint: ## Lint code with ruff
	ruff check .

format: ## Format code with black
	black .

check: ## Run Django system checks
	python manage.py check --deploy

superuser: ## Create a superuser
	python manage.py createsuperuser

messages: ## Generate translation message files
	python manage.py makemessages -l fr -l en
	python manage.py compilemessages
