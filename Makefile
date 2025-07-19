.PHONY: help build up down stop logs logs-web shell manage makemigrations migrate createsuperuser test lint format clean

# ตัวแปร
COMPOSE_FILE = docker-compose.yml
PYTHON_VERSION = 3.13 # ควรตรงกับใน Dockerfile

help:
	@echo "  build             Build or rebuild services"
	@echo "  up                Create and start containers in detached mode"
	@echo "  start             Create and start containers (attached mode)"
	@echo "  down              Stop and remove containers, networks, and volumes (use with caution for volumes)"
	@echo "  stop              Stop services"
	@echo "  logs              View output from all containers"
	@echo "  logs-web          View output from the web container"
	@echo "  shell             Access the Django shell_plus in the web container"
	@echo "  manage CMD='...'  Run a Django manage.py command (e.g., make manage CMD='showmigrations')"
	@echo "  makemigrations [APP=...] Create new database migrations (e.g., make makemigrations APP=my_app)"
	@echo "  migrate           Apply database migrations"
	@echo "  createsuperuser   Create a Django superuser (uses .env vars or prompts)"
	@echo "  test [APP=...]    Run tests (e.g., make test APP=my_app)"
	@echo "  lint              Lint the codebase (e.g., with flake8)"
	@echo "  format            Format the codebase (e.g., with black, isort)"
	@echo "  clean             Remove build artifacts and __pycache__"
	@echo "  prune             Stop containers and remove ALL related Docker resources (images, volumes, networks) - USE WITH EXTREME CAUTION"

# Docker Compose commands
DOCKER_COMPOSE = docker-compose -f $(COMPOSE_FILE) 

build:
	$(DOCKER_COMPOSE) build

build-clean:
	docker-compose build --no-cache

up: build
	$(DOCKER_COMPOSE) up -d --remove-orphans

start: build
	$(DOCKER_COMPOSE) up --remove-orphans

restart:
	$(DOCKER_COMPOSE) restart

down:
	$(DOCKER_COMPOSE) down -v --remove-orphans # -v removes volumes, be careful

stop:
	$(DOCKER_COMPOSE) stop

logs:
	$(DOCKER_COMPOSE) logs -f $(TARGET)

logs-web:
	$(DOCKER_COMPOSE) logs -f django

# Django specific commands
WEB_EXEC = $(DOCKER_COMPOSE) exec web

manage:
ifndef CMD
	@echo "Usage: make manage CMD=<your_manage.py_command>"
	@exit 1
endif
	$(WEB_EXEC) python manage.py $(CMD)

shell:
	$(WEB_EXEC) python manage.py shell_plus --ipython # หรือ python manage.py shell

makemigrations:
ifdef APP
	$(WEB_EXEC) python manage.py makemigrations $(APP)
else
	$(WEB_EXEC) python manage.py makemigrations
endif

migrate:
	$(WEB_EXEC) python manage.py migrate

createsuperuser:
	$(WEB_EXEC) python manage.py createsuperuser \
		--username $$(DJANGO_SUPERUSER_USERNAME) \
		--email $$(DJANGO_SUPERUSER_EMAIL) \
		--noinput || $(WEB_EXEC) python manage.py createsuperuser

test:
ifdef APP
	$(WEB_EXEC) python manage.py test $(APP)
else
	$(WEB_EXEC) python manage.py test
endif

# Python development tools (ensure they are in Pipfile/requirements.txt)
lint:
	@echo "Linting..."
	$(WEB_EXEC) flake8 .

format:
	@echo "Formatting..."
	$(WEB_EXEC) black .
	$(WEB_EXEC) isort .

clean:
	@echo "Removing __pycache__ and .pytest_cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .coverage htmlcov/

prune: stop
	@echo "WARNING: This will remove all Docker containers, networks, volumes, and images associated with this project."
	@read -p "Are you sure you want to continue? (yes/N): " confirm && [ $${confirm:-N} = yes ] || exit 1
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans
	@echo "Docker resources pruned."

# Initialize Django project (if it doesn't exist)
# This is a bit tricky as it needs to run once.
# init-django:
#   # Ensure Dockerfile doesn't try to copy a non-existent project first
#   $(DOCKER_COMPOSE) run --rm --entrypoint "" web django-admin startproject my_large_async_project_temp .
#   # Then manually move files or adjust Dockerfile and rebuild. This is often done manually once.
