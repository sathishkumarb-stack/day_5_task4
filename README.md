# Day 5 Task 4 – Integration Tests and Demo

## Project Overview
This project implements a Customer Management API using FastAPI and SQLAlchemy. It includes API key authentication, customer CRUD operations, pagination, webhook signature verification, and integration testing.

## Technologies Used
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pytest
- Pytest-Cov
- HTTPX

## Project Structure
```text
day5_task4/
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_main.py
├── .env.example
├── .gitignore
└── pyproject.toml
```

## Installation

1. Create a virtual environment:
   `py -m venv venv`

2. Activate it:
   `.\venv\Scripts\Activate.ps1`

3. Install dependencies:
   `py -m pip install -e ".[dev]"`

4. Configure the `.env` file using `.env.example`.

## Run the API
`py -m uvicorn src.main:app --reload`

Open Swagger documentation:
`http://127.0.0.1:8000/docs`

## Run Integration Tests
`py -m pytest -v`

## Run Coverage Report
`py -m pytest --cov=src --cov-report=term-missing`

## Test Results
- Total tests: 12
- Passed: 12
- Failed: 0
- Code coverage: 91%

## Tested Scenarios
- Health check
- Customer creation
- Customer listing
- Customer update
- Customer deletion
- Missing API key (401)
- Customer not found (404)
- Duplicate email (409)
- Invalid customer data (422)
- Valid webhook signature
- Tampered webhook signature
- Missing webhook signature

## Security
API keys and webhook secrets are configured through environment variables. The `.env` file is excluded from Git.

## Conclusion
All 12 integration tests passed successfully with 91% overall code coverage.