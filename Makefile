# Makefile for Obsidian Scribe development tasks

# Variables
PYTHON := python
PIP := pip
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Obsidian Scribe Development Tasks$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

.PHONY: install
install: ## Install the package in development mode
	@echo "$(BLUE)Installing Obsidian Scribe in development mode...$(NC)"
	$(PIP) install -e .

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install -e ".[dev]"

.PHONY: install-all
install-all: ## Install all dependencies (including dev and docs)
	@echo "$(BLUE)Installing all dependencies...$(NC)"
	$(PIP) install -e ".[dev,docs]"

.PHONY: clean
clean: ## Clean up build artifacts and cache files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/

.PHONY: format
format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	black $(SRC_DIR)
	@echo "$(GREEN)Code formatted!$(NC)"

.PHONY: lint
lint: ## Run linting with flake8
	@echo "$(BLUE)Running linter...$(NC)"
	flake8 $(SRC_DIR) --max-line-length=100 --extend-ignore=E203,W503

.PHONY: type-check
type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(NC)"
	mypy $(SRC_DIR) --ignore-missing-imports

.PHONY: test
test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	pytest $(TEST_DIR) -v

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term

.PHONY: check
check: lint type-check test ## Run all checks (lint, type-check, test)
	@echo "$(GREEN)All checks passed!$(NC)"

.PHONY: run
run: ## Run the application
	@echo "$(BLUE)Starting Obsidian Scribe...$(NC)"
	$(PYTHON) -m obsidian_scribe

.PHONY: run-debug
run-debug: ## Run the application in debug mode
	@echo "$(BLUE)Starting Obsidian Scribe in debug mode...$(NC)"
	$(PYTHON) -m obsidian_scribe --debug

.PHONY: watch
watch: ## Run the file watcher
	@echo "$(BLUE)Starting file watcher...$(NC)"
	$(PYTHON) -m obsidian_scribe watch

.PHONY: process
process: ## Process a specific audio file
	@echo "$(BLUE)Processing audio file...$(NC)"
	@read -p "Enter audio file path: " filepath; \
	$(PYTHON) -m obsidian_scribe process "$$filepath"

.PHONY: docs
docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd $(DOCS_DIR) && make html
	@echo "$(GREEN)Documentation built! Open $(DOCS_DIR)/_build/html/index.html$(NC)"

.PHONY: docs-serve
docs-serve: docs ## Build and serve documentation
	@echo "$(BLUE)Serving documentation...$(NC)"
	cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server

.PHONY: create-dirs
create-dirs: ## Create necessary directories
	@echo "$(BLUE)Creating directories...$(NC)"
	mkdir -p audio_input transcripts temp archive state cache logs
	@echo "$(GREEN)Directories created!$(NC)"

.PHONY: setup-config
setup-config: ## Set up configuration file
	@echo "$(BLUE)Setting up configuration...$(NC)"
	@if [ ! -f config.yaml ]; then \
		cp config.example.yaml config.yaml; \
		echo "$(GREEN)Created config.yaml from example$(NC)"; \
	else \
		echo "$(RED)config.yaml already exists$(NC)"; \
	fi

.PHONY: init
init: install-dev create-dirs setup-config ## Initialize development environment
	@echo "$(GREEN)Development environment initialized!$(NC)"

.PHONY: update-requirements
update-requirements: ## Update requirements.txt from setup.py
	@echo "$(BLUE)Updating requirements.txt...$(NC)"
	pip-compile setup.py -o requirements.txt
	@echo "$(GREEN)requirements.txt updated!$(NC)"

.PHONY: build
build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)Build complete!$(NC)"

.PHONY: publish-test
publish-test: build ## Publish to TestPyPI
	@echo "$(BLUE)Publishing to TestPyPI...$(NC)"
	twine upload --repository testpypi dist/*

.PHONY: publish
publish: build ## Publish to PyPI
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	@echo "$(RED)Are you sure you want to publish to PyPI? [y/N]$(NC)"
	@read -r response; \
	if [ "$$response" = "y" ]; then \
		twine upload dist/*; \
	else \
		echo "$(RED)Publishing cancelled$(NC)"; \
	fi

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t obsidian-scribe:latest .

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -it --rm \
		-v $(PWD)/audio_input:/app/audio_input \
		-v $(PWD)/transcripts:/app/transcripts \
		-v $(PWD)/config.yaml:/app/config.yaml \
		obsidian-scribe:latest

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install

# Development shortcuts
.PHONY: dev
dev: format lint type-check test ## Run all development checks

.PHONY: quick
quick: format lint ## Quick checks (format and lint only)

# Default target
.DEFAULT_GOAL := help