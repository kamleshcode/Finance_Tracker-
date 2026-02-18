# Personal Finance Tracker API

A professional, asynchronous RESTful API built with **FastAPI** and **MongoDB (Motor)**. This project implements a multi-module architecture to manage financial transactions and categories with high-performance search and aggregation.

---

## Project Structure

```text
Finance_Tracker/
├── finance_tracker/
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py            # MongoDB Connection & Indexing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py      # Category Pydantic Schemas
│   │   └── transaction.py   # Transaction Pydantic Schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── categories.py    # Category Endpoints
│   │   └── transactions.py  # Transaction Endpoints
│   ├── __init__.py
│   └── main.py              # App Entry Point & Starlette Hooks
├── pyproject.toml           # Dependency Management
└── README.md
```

# Tech Stack & Versions

*   **Python**: `>= 3.13`
*   **FastAPI**: `0.129.0` (Web Framework)
*   **Uvicorn**: `0.41.0` (ASGI Server)
*   **Motor**: `3.7.1` (Async MongoDB Driver)
*   **Pydantic**: `2.12.5` (Data Validation)

# API Endpoints

### Transactions
*   **POST** `/transactions`: Create a new financial record.
*   **GET** `/transactions`: List all transactions with built-in pagination.
*   **GET** `/transactions/{id}`: Retrieve full details for a single transaction.
*   **PATCH** `/transactions/{id}`: Partially update fields using the `TransactionUpdate` schema.
*   **DELETE** `/transactions/{id}`: Remove a specific transaction record.
*   **DELETE** `/transactions/bulk`: Mass delete records by category or specific date ranges.
*   **GET** `/transactions/search`: Perform a case-insensitive substring search on titles and descriptions.
*   **GET** `/transactions/summary`: Generate a monthly report including totals, balance, and category breakdowns.

### Categories
*   **POST** `/categories`: Register a new financial category.
*   **GET** `/categories`: View all available income and expense categories.
*   **PATCH** `/categories/{name}`: Update the description or type of an existing category.
*   **DELETE** `/categories/{name}`: Securely delete a category and reset linked transactions to "uncategorized".

# Dependency Management
This project uses **Poetry** for package management and virtual environment control.
*   **Virtual Environment**: Automatically managed in the `.venv` folder.
*   **Locking**: Uses `poetry.lock` to ensure all developers use the exact same versions of `FastAPI`, `Motor`, and `Pydantic`.
*   **Configuration**: Defined in `pyproject.toml`.

# Execution Commands

### 1. Install Dependencies
Run this command to set up your virtual environment and install all required packages:
```bash
poetry install
```
### 2.Run the Server
Run this command from the root Finance_Tracker directory:
```bash
poetry run uvicorn finance_tracker.main:app --reload
```


