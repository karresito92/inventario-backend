import pytest

def test_register_user(client):
    """Test: Registrar un nuevo usuario"""
    user_data = {
        "nombre": "Nuevo Usuario",
        "email": "nuevo@example.com",
        "contrasenia": "password123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nuevo@example.com"
    assert data["nombre"] == "Nuevo Usuario"
    assert "id_usuario" in data

def test_register_duplicate_email(client, test_user):
    """Test: No se puede registrar un email duplicado"""
    user_data = {
        "nombre": "Otro Usuario",
        "email": "test@example.com",  # Email ya existe
        "contrasenia": "password123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "ya esta registrado" in response.json()["detail"]

def test_login_success(client, test_user):
    """Test: Login exitoso devuelve token"""
    login_data = {
        "email": "test@example.com",
        "contrasenia": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Test: Login con contraseña incorrecta"""
    login_data = {
        "email": "test@example.com",
        "contrasenia": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "incorrecta" in response.json()["detail"]

def test_login_nonexistent_user(client):
    """Test: Login con usuario que no existe"""
    login_data = {
        "email": "noexiste@example.com",
        "contrasenia": "password123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]

def test_register_invalid_email(client):
    """Test: No se puede registrar con email invalido"""
    user_data = {
        "nombre": "Usuario Test",
        "email": "emailinvalido",
        "contrasenia": "password123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422