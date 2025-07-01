.PHONY: install test lint format clean run-worker run-demo start-temporal

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	black src/ tests/
	isort src/ tests/

format: lint

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

run-worker:
	python -m src.worker

run-demo:
	python -m src.demo

start-temporal:
	temporal server start-dev

demo: start-temporal
	@echo "Starting Temporal server..."
	@sleep 5
	@echo "Starting worker..."
	@python -m src.worker &
	@sleep 3
	@echo "Running demo..."
	@python -m src.demo
	@pkill -f "python -m src.worker"

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  install-dev  - Install dependencies with dev tools"
	@echo "  test         - Run tests"
	@echo "  lint         - Format code with black and isort"
	@echo "  clean        - Clean up Python cache files"
	@echo "  run-worker   - Start the Temporal worker"
	@echo "  run-demo     - Run the demo"
	@echo "  start-temporal - Start Temporal server"
	@echo "  demo         - Full demo (start server, worker, and run demo)" 