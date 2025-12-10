.PHONY: fmt lint test bundle all

fmt:
ruff format

lint:
ruff check --fix

test:
pytest -q

bundle:
PYTHONPATH=project python -m src.utils.archive --project-root project

all: fmt lint test
