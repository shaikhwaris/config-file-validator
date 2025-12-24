.PHONY: help install install-dev test lint format clean validate

help:
	@echo "Config File Validator - Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run test suite"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code with black and isort"
	@echo "  make validate      - Validate example configs"
	@echo "  make clean         - Clean up generated files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest test_validator.py -v --cov=validator --cov-report=term-missing

test-html:
	pytest test_validator.py -v --cov=validator --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 validator.py test_validator.py --max-line-length=120 --extend-ignore=E203,W503
	pylint validator.py test_validator.py --max-line-length=120 --disable=C0111

format:
	black validator.py test_validator.py --line-length=120
	isort validator.py test_validator.py

validate:
	@echo "Validating example configs..."
	@python validator.py examples/ || true

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov .tox dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

