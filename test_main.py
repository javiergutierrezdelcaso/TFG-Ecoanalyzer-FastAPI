import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ─────────────────────────────────────────────
# Health checks
# ─────────────────────────────────────────────
def test_root_devuelve_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_devuelve_timestamp():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


# ─────────────────────────────────────────────
# CRUD Items
# ─────────────────────────────────────────────
def test_listar_items_vacio():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_crear_item():
    payload = {"nombre": "Item test", "descripcion": "Descripción", "precio": 9.99}
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Item test"
    assert data["precio"] == 9.99
    assert "id" in data


def test_obtener_item_existente():
    # Primero crear
    payload = {"nombre": "Item obtener", "precio": 5.0}
    created = client.post("/items", json=payload).json()
    item_id = created["id"]

    # Luego obtener
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_obtener_item_no_existente():
    response = client.get("/items/99999")
    assert response.status_code == 404


def test_eliminar_item():
    # Crear
    payload = {"nombre": "Item borrar", "precio": 1.0}
    created = client.post("/items", json=payload).json()
    item_id = created["id"]

    # Eliminar
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200

    # Verificar que ya no existe
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404


def test_eliminar_item_no_existente():
    response = client.delete("/items/99999")
    assert response.status_code == 404
