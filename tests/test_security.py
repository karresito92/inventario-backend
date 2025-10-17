import pytest

def test_invalid_token(client):
    """Test: Token invalido es rechazado"""
    response = client.get("/products/my-products", params={"token": "token_invalido"})
    assert response.status_code == 401

def test_expired_token(client):
    """Test: Token expirado es rechazado"""
    # Token JWT que ya expiro
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxfQ.invalid"
    response = client.get("/products/my-products", params={"token": expired_token})
    assert response.status_code == 401

def test_cannot_update_other_user_product(client, test_product):
    """Test: No se puede editar el producto de otro usuario"""
    # Crear segundo usuario
    user2_data = {
        "nombre": "Usuario Dos",
        "email": "user2@example.com",
        "contrasenia": "password123"
    }
    client.post("/auth/register", json=user2_data)
    login_response = client.post("/auth/login", json={
        "email": "user2@example.com",
        "contrasenia": "password123"
    })
    user2_token = login_response.json()["access_token"]
    
    # Intentar editar producto del primer usuario
    product_id = test_product["id_producto"]
    updated_data = {
        "nombre": "Intento de Edicion",
        "precio": 999.00,
        "estado": "nuevo"
    }
    response = client.put(
        f"/products/{product_id}",
        json=updated_data,
        params={"token": user2_token}
    )
    assert response.status_code == 403

def test_cannot_delete_other_user_product(client, test_product):
    """Test: No se puede eliminar el producto de otro usuario"""
    # Crear segundo usuario
    user3_data = {
        "nombre": "Usuario Tres",
        "email": "user3@example.com",
        "contrasenia": "password123"
    }
    client.post("/auth/register", json=user3_data)
    login_response = client.post("/auth/login", json={
        "email": "user3@example.com",
        "contrasenia": "password123"
    })
    user3_token = login_response.json()["access_token"]
    
    # Intentar eliminar producto del primer usuario
    product_id = test_product["id_producto"]
    response = client.delete(
        f"/products/{product_id}",
        params={"token": user3_token}
    )
    assert response.status_code == 403

def test_sql_injection_prevention_login(client):
    """Test: Prevencion de SQL injection en login"""
    malicious_data = {
        "email": "' OR '1'='1",
        "contrasenia": "' OR '1'='1"
    }
    response = client.post("/auth/login", json=malicious_data)
    assert response.status_code in [404, 401, 422]

def test_xss_prevention_product_name(client, auth_token):
    """Test: Prevencion de XSS en nombre de producto"""
    xss_data = {
        "nombre": "<script>alert('XSS')</script>",
        "precio": 100.00,
        "estado": "nuevo"
    }
    response = client.post(
        "/products/publish",
        json=xss_data,
        params={"token": auth_token}
    )
    # El producto se crea pero el script es tratado como texto
    if response.status_code == 200:
        data = response.json()
        # El nombre no debe ejecutarse como codigo
        assert "<script>" in data["nombre"] or data["nombre"] == "<script>alert('XSS')</script>"

def test_cannot_delete_sold_product(client, auth_token, test_product):
    """Test: No se puede eliminar un producto ya vendido"""
    # Crear comprador
    buyer_data = {
        "nombre": "Comprador Test",
        "email": "buyer@example.com",
        "contrasenia": "password123"
    }
    client.post("/auth/register", json=buyer_data)
    login_response = client.post("/auth/login", json={
        "email": "buyer@example.com",
        "contrasenia": "password123"
    })
    buyer_token = login_response.json()["access_token"]
    
    # Comprar el producto
    product_id = test_product["id_producto"]
    client.post(f"/orders/buy/{product_id}", params={"token": buyer_token})
    
    # Intentar eliminarlo
    response = client.delete(
        f"/products/{product_id}",
        params={"token": auth_token}
    )
    assert response.status_code == 400
    assert "vendido" in response.json()["detail"]

def test_password_not_returned_in_response(client):
    """Test: La contrasena no se devuelve en las respuestas"""
    user_data = {
        "nombre": "Security Test",
        "email": "security@example.com",
        "contrasenia": "securepassword123"
    }
    response = client.post("/auth/register", json=user_data)
    data = response.json()
    assert "contrasenia" not in data
    assert "password" not in str(data).lower()