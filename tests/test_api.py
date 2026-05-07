import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use a separate test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_register_user():
    response = client.post("/auth/register", json={
        "username": "testuser1",
        "email": "testuser1@email.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser1"

def test_register_duplicate_user():
    client.post("/auth/register", json={
        "username": "duplicateuser",
        "email": "duplicate@email.com",
        "password": "password123"
    })
    response = client.post("/auth/register", json={
        "username": "duplicateuser",
        "email": "duplicate@email.com",
        "password": "password123"
    })
    assert response.status_code == 400

def test_login_user():
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "loginuser@email.com",
        "password": "password123"
    })
    response = client.post("/auth/login", data={
        "username": "loginuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_product():
    client.post("/auth/register", json={
        "username": "productuser",
        "email": "productuser@email.com",
        "password": "password123"
    })
    login = client.post("/auth/login", data={
        "username": "productuser",
        "password": "password123"
    })
    token = login.json()["access_token"]
    response = client.post("/products/",
        json={
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "stock": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Product"

def test_create_product_invalid_price():
    client.post("/auth/register", json={
        "username": "priceuser",
        "email": "priceuser@email.com",
        "password": "password123"
    })
    login = client.post("/auth/login", data={
        "username": "priceuser",
        "password": "password123"
    })
    token = login.json()["access_token"]
    response = client.post("/products/",
        json={
            "name": "Bad Product",
            "description": "Invalid price",
            "price": -10.00,
            "stock": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_get_products():
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unauthorized_create_product():
    response = client.post("/products/", json={
        "name": "Unauthorized Product",
        "description": "Should fail",
        "price": 50.00,
        "stock": 5
    })
    assert response.status_code == 401