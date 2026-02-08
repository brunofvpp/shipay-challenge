PROJECT_NAME := shipay_challenge_app
PYTHON_VERSION := 3.12.10
VENV_NAME := shipay_challenge-$(PYTHON_VERSION)

.PHONY: logs test test-e2e-postgres format update clean docs

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | sed -e 's/\(\:.*\#\#\)/\:\ /' | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

.clean-pyc: ## remove python file artifacts
	find . -name '*.pyc' -exec rm -v -f {} +
	find . -name '*.pyo' -exec rm -v -f {} +
	find . -name '*~' -exec rm -v -f {} +
	find . -name '__pycache__' -exec rm -v -fr {} +

.clean-build: ## remove build artifacts
	rm -v -fr build/
	rm -v -fr dist/
	rm -v -fr .eggs/
	find . -name '*.egg-info' -exec rm -v -fr {} +
	find . -name '*.egg' -exec rm -v -f {} +

.clean-test: ## remove test and coverage artifacts
	rm -v -fr .tox/
	rm -v -f .coverage
	rm -v -fr htmlcov/
	rm -v -fr reports/
	rm -v -fr .pytest_cache/
	rm -v -f coverage.xml

clean: .clean-build .clean-pyc .clean-test ## remove all build, test, coverage and python artifacts

create-venv: ## install python, create virtualenv and set virtualenv to current
	pyenv install -s $(PYTHON_VERSION)
	pyenv uninstall -f $(VENV_NAME)
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME)
	pyenv local $(VENV_NAME)
	pip install -U pip poetry

setup: ## install only prod requirements
	poetry install --no-root --only main

setup-dev: ## install all requirements
	poetry install --no-root

build: ## up all containers and building the project image
	docker compose up -d --build

up: ## up all containers
	docker compose up -d

down: ## down all containers
	docker compose down
	docker compose rm

recreate: down up ## recreate containers

bash: ## run container bash
	docker exec -it $(PROJECT_NAME) bash

migrations: ## create migration file
	docker exec -it $(PROJECT_NAME) sh -c "cd /app && /opt/venv/bin/python -m alembic revision --autogenerate"

migrate: ## run migratrion
	docker exec -it $(PROJECT_NAME) sh -c "cd /app && /opt/venv/bin/python -m alembic upgrade head"

logs: ## project logs on container
	docker logs $(PROJECT_NAME) --follow

test:  ## running tests
	docker compose up -d shipay_challenge_database
	docker exec -it $(PROJECT_NAME) sh -c "cd /app && /opt/venv/bin/python -m pytest"

ruff: ## run ruff
	ruff check --select I --fix src tests
	ruff format src tests

update:
	@echo "🔄 Updating dependencies..."
	poetry update
	@echo "✅ Dependencies updated successfully!"
