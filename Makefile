.PHONY: setup up down lint format test test-cov eval run clean

setup:
	uv venv
	uv pip install -e ".[dev]"
	uv run pre-commit install

up:
	docker compose up -d

down:
	docker compose down

lint:
	uv run ruff check .
	uv run mypy src

format:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest tests/unit

test-cov:
	uv run pytest --cov=src --cov-report=term-missing

eval:
	uv run python -m rag_app.evaluation.run

run:
	uv run streamlit run src/rag_app/app/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
