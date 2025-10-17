import pytest

def test_get_catalog(client, test_product):
    """Test: Obtener catalogo de productos disponibles"""
    response = client.get("/products/catalog")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["vendido"] == False

def test_publish_product(client, auth_token):
    """Test: Publicar un nuevo producto"""
    product_data = {
        "nombre": "Laptop HP",
        "marca": "HP",
        "descripcion": "Laptop en buen estado",
        "precio": 300.00,
        "estado": "usado",
        "imagen_url": None
    }
    response = client.post(
        "/products/publish",
        json=product_data,
        params={"token": auth_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Laptop HP"
    assert data["precio"] == 300.00
    assert data["vendido"] == False

def test_publish_product_without_token(client):
    """Test: No se puede publicar sin token"""
    product_data = {
        "nombre": "Producto",
        "precio": 100.00,
        "estado": "nuevo"
    }
    response = client.post("/products/publish", json=product_data)
    assert response.status_code == 422

def test_get_my_products(client, auth_token, test_product):
    """Test: Obtener mis productos publicados"""
    response = client.get("/products/my-products", params={"token": auth_token})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_update_product(client, auth_token, test_product):
    """Test: Actualizar un producto propio"""
    product_id = test_product["id_producto"]
    updated_data = {
        "nombre": "Producto Actualizado",
        "marca": "Marca Nueva",
        "descripcion": "Descripcion actualizada",
        "precio": 75.00,
        "estado": "como nuevo",
        "imagen_url": None
    }
    response = client.put(
        f"/products/{product_id}",
        json=updated_data,
        params={"token": auth_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Producto Actualizado"
    assert data["precio"] == 75.00

def test_update_nonexistent_product(client, auth_token):
    """Test: No se puede actualizar un producto que no existe"""
    updated_data = {
        "nombre": "Producto",
        "precio": 100.00,
        "estado": "nuevo"
    }
    response = client.put(
        "/products/99999",
        json=updated_data,
        params={"token": auth_token}
    )
    assert response.status_code == 404

def test_delete_product(client, auth_token):
    """Test: Eliminar un producto propio"""
    # Crear producto para eliminar
    product_data = {
        "nombre": "Para Eliminar",
        "precio": 50.00,
        "estado": "nuevo"
    }
    create_response = client.post(
        "/products/publish",
        json=product_data,
        params={"token": auth_token}
    )
    product_id = create_response.json()["id_producto"]
    
    # Eliminar producto
    response = client.delete(
        f"/products/{product_id}",
        params={"token": auth_token}
    )
    assert response.status_code == 200
    assert "eliminado exitosamente" in response.json()["message"]

def test_delete_nonexistent_product(client, auth_token):
    """Test: No se puede eliminar un producto que no existe"""
    response = client.delete(
        "/products/99999",
        params={"token": auth_token}
    )
    assert response.status_code == 404

def test_buy_product(client, auth_token, test_product):
    """Test: Comprar un producto disponible"""
    # Crear segundo usuario (comprador)
    buyer_data = {
        "nombre": "Comprador",
        "email": "comprador@example.com",
        "contrasenia": "password123"
    }
    client.post("/auth/register", json=buyer_data)
    
    # Login del comprador
    login_response = client.post("/auth/login", json={
        "email": "comprador@example.com",
        "contrasenia": "password123"
    })
    buyer_token = login_response.json()["access_token"]
    
    # Comprar producto
    product_id = test_product["id_producto"]
    response = client.post(
        f"/orders/buy/{product_id}",
        params={"token": buyer_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["vendido"] == True

def test_buy_own_product(client, auth_token, test_product):
    """Test: No se puede comprar tu propio producto"""
    product_id = test_product["id_producto"]
    response = client.post(
        f"/orders/buy/{product_id}",
        params={"token": auth_token}
    )
    assert response.status_code == 400
    assert "tu propio producto" in response.json()["detail"]

def test_catalog_does_not_show_sold_products(client, auth_token, test_product):
    """Test: El catalogo no muestra productos vendidos"""
    # Crear comprador y comprar el producto
    buyer_data = {
        "nombre": "Comprador Dos",
        "email": "comprador2@example.com",
        "contrasenia": "password123"
    }
    client.post("/auth/register", json=buyer_data)
    login_response = client.post("/auth/login", json={
        "email": "comprador2@example.com",
        "contrasenia": "password123"
    })
    buyer_token = login_response.json()["access_token"]
    
    product_id = test_product["id_producto"]
    client.post(f"/orders/buy/{product_id}", params={"token": buyer_token})
    
    # Verificar que no aparece en el catalogo
    catalog_response = client.get("/products/catalog")
    catalog_products = catalog_response.json()
    product_ids = [p["id_producto"] for p in catalog_products]
    assert product_id not in product_ids