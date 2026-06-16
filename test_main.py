import pytest  # noqa: F401
from fastapi.testclient import TestClient
from main import app, analisis_db, calcular_nivel_impacto

client = TestClient(app)


# ═══════════════════════════════════════════════════════════
# PRUEBAS UNITARIAS
# Validan funciones y lógica interna de forma aislada
# ═══════════════════════════════════════════════════════════

class TestCalcularNivelImpacto:
    """Pruebas unitarias de la función calcular_nivel_impacto"""

    def test_nivel_bajo(self):
        assert calcular_nivel_impacto(5.0) == "bajo"

    def test_nivel_bajo_limite(self):
        assert calcular_nivel_impacto(9.99) == "bajo"

    def test_nivel_medio(self):
        assert calcular_nivel_impacto(25.0) == "medio"

    def test_nivel_medio_limite_inferior(self):
        assert calcular_nivel_impacto(10.0) == "medio"

    def test_nivel_medio_limite_superior(self):
        assert calcular_nivel_impacto(49.99) == "medio"

    def test_nivel_alto(self):
        assert calcular_nivel_impacto(100.0) == "alto"

    def test_nivel_alto_limite_inferior(self):
        assert calcular_nivel_impacto(50.0) == "alto"

    def test_nivel_alto_limite_superior(self):
        assert calcular_nivel_impacto(199.99) == "alto"

    def test_nivel_critico(self):
        assert calcular_nivel_impacto(500.0) == "critico"

    def test_nivel_critico_limite(self):
        assert calcular_nivel_impacto(200.0) == "critico"

    def test_valor_muy_pequeno(self):
        assert calcular_nivel_impacto(0.01) == "bajo"

    def test_valor_muy_grande(self):
        assert calcular_nivel_impacto(99999.0) == "critico"


# ═══════════════════════════════════════════════════════════
# PRUEBAS DE INTEGRACIÓN — Health y Landing
# Verifican endpoints de estado del servicio
# ═══════════════════════════════════════════════════════════

class TestHealthYLanding:

    def test_landing_devuelve_html(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_landing_contiene_nombre_servicio(self):
        response = client.get("/")
        assert "EcoAnalyzer" in response.text

    def test_landing_contiene_entorno(self):
        response = client.get("/")
        assert "ENTORNO" in response.text

    def test_landing_contiene_links_api(self):
        response = client.get("/")
        assert "/docs" in response.text
        assert "/health" in response.text
        assert "/analisis" in response.text

    def test_health_devuelve_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_contiene_campos_requeridos(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "entorno" in data
        assert "kv_conectado" in data
        assert "timestamp" in data

    def test_health_status_es_ok(self):
        response = client.get("/health")
        assert response.json()["status"] == "ok"


# ═══════════════════════════════════════════════════════════
# PRUEBAS DE INTEGRACIÓN — Categorías
# ═══════════════════════════════════════════════════════════

class TestCategorias:

    def test_listar_categorias_devuelve_200(self):
        response = client.get("/categorias")
        assert response.status_code == 200

    def test_listar_categorias_contiene_cuatro(self):
        response = client.get("/categorias")
        assert len(response.json()["categorias"]) == 4

    def test_categorias_contiene_energia(self):
        response = client.get("/categorias")
        ids = [c["id"] for c in response.json()["categorias"]]
        assert "energia" in ids

    def test_categorias_contiene_transporte(self):
        response = client.get("/categorias")
        ids = [c["id"] for c in response.json()["categorias"]]
        assert "transporte" in ids

    def test_categorias_contiene_residuos(self):
        response = client.get("/categorias")
        ids = [c["id"] for c in response.json()["categorias"]]
        assert "residuos" in ids

    def test_categorias_contiene_agua(self):
        response = client.get("/categorias")
        ids = [c["id"] for c in response.json()["categorias"]]
        assert "agua" in ids

    def test_categorias_tienen_descripcion(self):
        response = client.get("/categorias")
        for cat in response.json()["categorias"]:
            assert "descripcion" in cat
            assert len(cat["descripcion"]) > 0


# ═══════════════════════════════════════════════════════════
# PRUEBAS DE INTEGRACIÓN — CRUD Análisis
# ═══════════════════════════════════════════════════════════

class TestAnalisisCRUD:

    def setup_method(self):
        """Limpiar la base de datos antes de cada test"""
        analisis_db.clear()

    def test_listar_analisis_vacio(self):
        response = client.get("/analisis")
        assert response.status_code == 200
        assert response.json() == []

    def test_crear_analisis_exitoso(self):
        payload = {
            "nombre": "Consumo oficina",
            "categoria": "energia",
            "valor_co2_kg": 45.5
        }
        response = client.post("/analisis", json=payload)
        assert response.status_code == 201

    def test_crear_analisis_devuelve_id(self):
        payload = {
            "nombre": "Viaje en coche",
            "categoria": "transporte",
            "valor_co2_kg": 12.0
        }
        data = client.post("/analisis", json=payload).json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_crear_analisis_asigna_nivel_impacto(self):
        payload = {
            "nombre": "Residuos semanales",
            "categoria": "residuos",
            "valor_co2_kg": 5.0
        }
        data = client.post("/analisis", json=payload).json()
        assert data["nivel_impacto"] == "bajo"

    def test_crear_analisis_nivel_impacto_critico(self):
        payload = {
            "nombre": "Fábrica industrial",
            "categoria": "energia",
            "valor_co2_kg": 500.0
        }
        data = client.post("/analisis", json=payload).json()
        assert data["nivel_impacto"] == "critico"

    def test_crear_analisis_con_descripcion(self):
        payload = {
            "nombre": "Test",
            "categoria": "agua",
            "valor_co2_kg": 3.0,
            "descripcion": "Descripción detallada"
        }

    valores = [a.valor_co2_kg for a in analisis_db.values()]
    por_categoria: dict = {}
    por_nivel: dict = {}

    for a in analisis_db.values():
        por_categoria[a.categoria] = (
            por_categoria.get(a.categoria, 0) + a.valor_co2_kg
        )
        por_nivel[a.nivel_impacto] = por_nivel.get(a.nivel_impacto, 0) + 1

    return {
        "total_analisis": len(analisis_db),
        "co2_total_kg": round(sum(valores), 2),
        "co2_promedio_kg": round(sum(valores) / len(valores), 2),
        "co2_maximo_kg": round(max(valores), 2),
        "co2_minimo_kg": round(min(valores), 2),
        "por_categoria": {k: round(v, 2) for k, v in por_categoria.items()},
        "por_nivel_impacto": por_nivel,
    }
