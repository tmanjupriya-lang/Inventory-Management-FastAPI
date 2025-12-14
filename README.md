# Inventory Management FastAPI

A backend **Inventory Management REST API** built using **FastAPI**. This project demonstrates real‑world backend development practices including **JWT authentication**, **role‑based access control (RBAC)**, **database migrations with Alembic**, and **API testing using Pytest**.

This repository is designed as a **portfolio‑ready project** to showcase hands‑on experience with Python backend development.

---

## Tech Stack

* **Python**
* **FastAPI**
* **PostgreSQL**
* **SQLAlchemy (Core usage)**
* **Alembic** – database migrations
* **JWT (OAuth2 Password Flow)** – authentication
* **Pytest** – API testing

---

## Key Features

* User registration and login
* JWT access token generation and validation
* Role‑based access control (Admin / Manager / User)
* Inventory CRUD operations
* Secure protected routes based on roles
* Database schema versioning using Alembic
* Centralized logging
* Automated API tests using Pytest

---

## Project Structure

```
InventoryManagement/
│
├── app/
│   ├── Router/          # API route definitions
│   ├── Repository/      # Database access logic
│   ├── auth/            # JWT auth & permissions
│   ├── schema/          # Pydantic request/response models
│   ├── Logger/          # Logging configuration
│   ├── connection.py    # Database connection
│   ├── models.py        # DB models
│   ├── utils.py         # Utility functions
│   └── main.py          # FastAPI app entry point
│
├── tests/               # Pytest test cases
├── alembic/             # Database migrations
├── alembic.ini
├── .gitignore
└── README.md
```

---

## Setup & Run Locally

### 1️ Clone the repository

```bash
git clone https://github.com/tmanjupriya-lang/Inventory-Management-FastAPI.git
cd InventoryManagement
```

### 2️ Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3️ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️ Configure environment variables

Create a `.env` file (not committed to Git) with required values such as:

```
DATABASE_URL=
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5️ Run database migrations

```bash
alembic upgrade head
```

### 6️ Start the server

```bash
uvicorn app.main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI provides built‑in interactive documentation:

* **Swagger UI** → `http://127.0.0.1:8000/docs`
* **ReDoc** → `http://127.0.0.1:8000/redoc`

---

## Testing

API tests are written using **Pytest**.

Covered areas:

* Authentication flow
* Role‑based access validation
* Inventory endpoints

Run tests using:

```bash
pytest -v
```

---

## Authentication & Authorization

* OAuth2 password flow is used for authentication
* JWT tokens are issued on login
* Protected routes validate token and user roles

Roles supported:

* **Admin**
* **Manager**
* **User**

---

## Future Enhancements

* Dockerization
* CI/CD pipeline integration
* Pagination & filtering
* Refresh token rotation
* Deployment on cloud (AWS / Railway / Render)

---

## Author

**Manjupriya Thangavelu**
Backend Developer | Python | FastAPI

---

If you find this project useful, feel free to star the repository!
