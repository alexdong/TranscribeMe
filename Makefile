.PHONY: help install test lint format check clean dev

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync --dev

dev: ## Start development server
	uv run python -m transcribe_me.main

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=src/transcribe_me --cov-report=html --cov-report=term

lint: ## Run linting
	uv run ruff check .

format: ## Format code
	uv run black .
	uv run ruff check --fix .

check: ## Run all checks (lint + format check + tests)
	uv run ruff check .
	uv run black --check .
	uv run pytest

clean: ## Clean up cache and build artifacts
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete