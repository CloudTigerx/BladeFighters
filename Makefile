# Convenience developer tasks

PY?=.venv/bin/python
PIP?=.venv/bin/pip
PKG=swordfighting_new

.PHONY: help venv install run test cov clean cache-clean

help:
	@echo 'Common targets:'
	@echo '  make venv        - create virtualenv (.venv)'
	@echo '  make install     - install dev dependencies'
	@echo '  make run         - run pygame client'
	@echo '  make test        - run pytest'
	@echo '  make cov         - run pytest with coverage summary'
	@echo '  make clean       - remove pyc/__pycache__'

venv:
	@test -d .venv || python3 -m venv .venv
	@echo 'Virtualenv ready.'

install: venv
	$(PIP) install -r requirements-dev.txt || true

run:
	$(PY) -m $(PKG).pygame_client

test:
	$(PY) -m pytest -q

cov:
	$(PY) -m pytest --cov=$(PKG) --cov-report=term-missing -q

clean:
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	@find . -name '*.pyc' -delete
	@echo 'Cleaned.'
