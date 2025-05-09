# Exchange API

This project implements a RESTful API for currency conversion, with user authentication, session management, and logging of performed transactions.

## Purpose

The Exchange API was developed to provide a currency conversion service using an external API. The goal is to allow users to perform conversions between different currencies (BRL, USD, EUR, JPY) and maintain a history of completed transactions. Additionally, the API provides login and logout functionalities to ensure user authentication.

## Features

- **Currency Conversion**: Allows users to convert between different currencies (BRL, USD, EUR, JPY).
- **User Authentication**: Login and logout functionalities with session management.
- **Transaction History**: Users can view their past currency conversion transactions.
- **Transaction Logging**: The API logs all transactions with details such as currencies involved, conversion amount, and exchange rate.

## Technologies Used

- **FastAPI**: A modern, high-performance framework for building RESTful APIs with Python.
- **SQLAlchemy**: ORM library for efficiently working with relational databases.
- **Pydantic**: For data validation and model management.
- **SQLite**: In-memory database used for testing and local development.
- **pytest**: Testing framework to ensure API functionality.

## Motivation for Technology Choices

- **FastAPI** was chosen for its high performance, ease of use, and asynchronous support, which is important for optimizing communication with the external currency API.
- **SQLAlchemy** abstracts database communication, ensuring fast development and clean, maintainable code.
- **Pydantic** is used to validate input and output data, ensuring the API handles valid data.
- **SQLite** is used as an in-memory database during development for a fast and isolated testing environment.
- **pytest** is used to ensure that all API features are well tested and function as expected.

## Project Structure

The project is organized to clearly separate the application layers. Below is a summary of the main folders and files:

```
.
├── app/
│   ├── controllers/         # Controllers responsible for API routes
│   │   ├── exchange_controller.py
│   │   ├── user_controller.py
│   │   └── login_controller.py
│   ├── entities/            # Data models and database table definitions
│   │   ├── entity.py
│   ├── gateways/            # Communication with external APIs and the database
│   │   ├── database/        # Database configuration and connectors
│   │   ├── external_api/    # Currency conversion API
│   ├── schemas/             # Schemas for data validation
│   ├── services/            # Business logic
│   │   ├── auth_service.py  # Authentication logic
│   ├── utils/               # Utility functions and middleware
│   │   ├── auth_deps.py     # Authentication dependencies
│   │   ├── config/          # Logging and global settings
├── tests/                   # Unit and integration tests
│   ├── test_current_conversion.py
│   ├── test_login_logout.py
│   └── test_transaction_repository.py
├── main.py                  # Main file for starting the application
├── requirements.txt         # Project dependencies
└── README.md                # This file
```


## Application Layers

- **Controllers**: Handle HTTP requests and return responses. Define routes and control flow logic (e.g., `exchange_controller.py`, `user_controller.py`).
- **Entities**: Define data models to be persisted in the database (e.g., `User`, `CurrencyConversionTransaction`).
- **Gateways**: Interact with the database and external APIs (e.g., external currency API, SQLite with SQLAlchemy).
- **Services**: Contain business logic (e.g., `auth_service.py` for user authentication).
- **Schemas**: Define input and output validation schemas using Pydantic.
- **Utils**: Include helper functions and middleware (e.g., logging, global settings, authentication logic).

## How to Run the Application

Clone the repository:

```bash
git clone https://github.com/your-username/exchange-api.git
cd exchange-api
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

**On Windows:**

```bash
.venv\Scripts\activate
```

**On Linux/macOS:**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn app.main:app --reload
```

Access the API:

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000). You can view the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API Documentation

Access after starting:

- **Swagger UI**: http://127.0.0.1:8000/docs

- **Redoc**: http://127.0.0.1:8000/redoc


## How to Run the Tests

Install the test dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the tests:

```bash
 pytest -v test/
```

## Contributions

Contributions are welcome! If you’d like to contribute to the project, fork it, create a branch for your changes, and submit a pull request.