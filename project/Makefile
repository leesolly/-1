.PHONY: fmt lint test all

fmt:
ruff format

lint:
ruff check --fix

test:
pytest -q

all: fmt lint test
