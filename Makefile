VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
FLAKE8=$(VENV)/bin/flake8
BLACK=$(VENV)/bin/black
ISORT=$(VENV)/bin/isort

.PHONY: venv install lint fmt run dev test test-unit test-integration test-all weather weather-current weather-historical weather-summary weather-outdoor forecast forecast-today forecast-week forecast-summary

venv:
	python3 -m venv $(VENV)

install: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-dev.txt

lint:
	$(FLAKE8) .

fmt:
	$(BLACK) .
	$(ISORT) .

run:
	$(PYTHON) -m home_automation_service.app

dev: install run

test: test-all

test-unit: install
	$(PYTHON) -m pytest tests/unit/ -v

test-integration: install
	$(PYTHON) -m pytest tests/integration/ -v

test-all: install
	$(PYTHON) -m pytest tests/ -v

weather: install
	$(PYTHON) weather_cli.py

weather-current: install
	$(PYTHON) weather_cli.py --current

weather-historical: install
	$(PYTHON) weather_cli.py --historical

weather-summary: install
	$(PYTHON) weather_cli.py --summary

weather-outdoor: install
	$(PYTHON) weather_cli.py --outdoor

forecast: install
	$(PYTHON) forecast_cli.py

forecast-today: install
	$(PYTHON) forecast_cli.py --today

forecast-week: install
	$(PYTHON) forecast_cli.py --week

forecast-summary: install
	$(PYTHON) forecast_cli.py --summary


