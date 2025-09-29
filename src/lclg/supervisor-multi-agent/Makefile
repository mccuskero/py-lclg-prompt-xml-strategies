# Multi-Agent System Makefile

.PHONY: help install install-dev test lint format clean run examples setup

help: ## Show this help message
	@echo "Multi-Agent System Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

install-dev: ## Install development dependencies
	uv sync --dev

setup: ## Run complete setup
	python uv_setup.py

test: ## Run tests
	uv run pytest

test-system: ## Run system tests
	uv run python test_basic.py
	uv run python test_complex_coordination.py

lint: ## Run linting
	uv run ruff check .
	uv run black --check .

format: ## Format code
	uv run black .
	uv run isort .

run: ## Run interactive session
	uv run python main.py

examples: ## Run examples
	uv run python examples.py

example-prompts: ## Run example prompts demo
	uv run python example_prompts.py

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

dev: install-dev ## Install dev dependencies and run setup
	@echo "Development environment ready!"

check: lint test ## Run all checks (lint + test)

all: install-dev format lint test ## Run everything
