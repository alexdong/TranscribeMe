.PHONY: help install test test-unit test-integration test-sms test-api test-config test-all lint format check clean dev validate

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync --dev

dev: ## Start development server
	uv run python -m transcribe_me.main

test: ## Run all tests (unit + integration)
	uv run pytest

test-unit: ## Run unit tests only
	uv run pytest tests/test_main.py tests/test_phone_handler.py tests/test_transcription.py -v

test-integration: ## Run all integration tests
	uv run pytest tests/test_integration_*.py -v

test-sms: ## Run SMS integration tests (NZ mobile validation & SMS sending)
	@echo "Running SMS Integration Tests for NZ mobile numbers..."
	uv run pytest tests/test_integration_sms.py -v -s

test-api: ## Run API integration tests (webhooks & endpoints)
	@echo "Running API Integration Tests..."
	uv run pytest tests/test_integration_api.py -v -s

test-config: ## Run configuration integration tests
	@echo "Running Configuration Integration Tests..."
	uv run pytest tests/test_integration_config.py -v -s

test-all: ## Run comprehensive test suite with coverage
	@echo "Running Complete Test Suite..."
	uv run pytest --cov=src/transcribe_me --cov-report=html --cov-report=term-missing -v

validate: ## Run comprehensive validation (config + SMS + API tests)
	@echo "Running Comprehensive Validation..."
	@echo "1. Configuration Validation..."
	@make test-config
	@echo ""
	@echo "2. SMS Integration Validation..."
	@make test-sms
	@echo ""
	@echo "3. API Integration Validation..."
	@make test-api
	@echo ""
	@echo "Validation Complete!"

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
	rm -rf transcribeme.log
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete