.PHONY: setup check-uv build test clean clean_venv clean_build clean_cache format check type  

setup: check-uv uv.lock
	@echo "Setting up project..."
	uv sync

	
check-uv:
	@if ! command -v uv > /dev/null; then \
		echo "UV is not installed"; \
		echo "Installing UV"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi

test: tests/test_*.py
	@echo "Running tests on python3.10"
	@if ! uv run --python 3.10 pytest; then \
		echo "Tests failed. Building project not possible."; \
		exit 1; \
	fi
	@echo "Running tests on python3.11"
	@if ! uv run --python 3.11 pytest; then \
		echo "Tests failed. Building project not possible."; \
		exit 1; \
	fi
	@echo "Running tests on python3.12"
	@if ! uv run --python 3.12 pytest; then \
		echo "Tests failed. Building project not possible."; \
		exit 1; \
	fi

clean: clean_venv clean_build clean_cache

clean_venv:
	@echo "Removing virtual environment.."
	rm -rf .venv

clean_build:
	@echo "Removing build files..."
	rm -rf dist/

clean_cache:
	@echo "Removing all cache files and directories int the project..." 
	find . -name "*cache*" -type d | xargs -t -I {} rm -rf "{}"

format:
	@echo "Formatting project files with ruff..."
	uv run ruff format

check:
	@echo "Checking project files with ruff..."
	uv run ruff check

type:
	@echo "checking typing with mypy..."
	uv run mypy .