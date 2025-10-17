import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base, get_db
import os

# Configurar variable de entorno para tests
os.environ["TESTING"] = "1"

# Importar modelos
from app.models.user import User
from app.models.product import Product

# Base de datos SQLite en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    from app.main import app
    from fastapi.testclient import TestClient
    
    app.dependency_overrides[get_db] = override_get_db
    
    return TestClient(app)

@pytest.fixture
def test_user(client):
    user_data = {
        "nombre": "Test User",
        "email": "test@example.com",
        "contrasenia": "testpassword123"
    }
    response = client.post("/auth/register", json=user_data)
    return response.json()

@pytest.fixture
def auth_token(client, test_user):
    """Token JWT para usuario de prueba"""
    login_data = {
        "email": "test@example.com",
        "contrasenia": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)
    
    # Si el login falla, mostrar el error
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.json()}")
        raise Exception(f"Login failed with status {response.status_code}")
    
    return response.json()["access_token"]

@pytest.fixture
def test_product(client, auth_token):
    product_data = {
        "nombre": "Producto Test",
        "marca": "Marca Test",
        "descripcion": "Descripcion de prueba",
        "precio": 50.00,
        "estado": "nuevo",
        "imagen_url": None
    }
    response = client.post(
        "/products/publish",
        json=product_data,
        params={"token": auth_token}
    )
    return response.json()