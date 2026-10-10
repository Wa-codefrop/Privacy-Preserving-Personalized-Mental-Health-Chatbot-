.PHONY: install install-frontend test frontend-build lint ci

install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

install-frontend:
	npm --prefix frontend install --no-fund --no-audit

test:
	if [ -x .venv/bin/python ]; then .venv/bin/python -m pytest -q; else python3 -m pytest -q; fi

frontend-build:
	npm --prefix frontend run build

lint:
	if [ -x .venv/bin/python ]; then .venv/bin/python -m compileall backend; else python3 -m compileall backend; fi
	npm --prefix frontend run lint

ci: lint test frontend-build
