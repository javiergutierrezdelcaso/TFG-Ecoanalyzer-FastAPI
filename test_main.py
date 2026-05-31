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
        assert "servicio" in data
        assert "entorno" in data
        assert "version" in data
        assert "timestamp" in data

    def test_health_servicio_es_ecoanalyzer(self):
        response = client.get("/health")
        assert response.json()["servicio"] == "ecoanalyzer"

    def test_health_version_correcta(self):
        response = client.get("/health")
        assert response.json()["version"] == "1.0.0"


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
        data = client.post("/analisis", json=payload).json()
        assert data["descripcion"] == "Descripción detallada"

    def test_crear_analisis_categoria_invalida(self):
        payload = {
            "nombre": "Test inválido",
            "categoria": "nuclear",
            "valor_co2_kg": 10.0
        }
        response = client.post("/analisis", json=payload)
        assert response.status_code == 422

    def test_crear_analisis_co2_negativo(self):
        payload = {
            "nombre": "Test negativo",
            "categoria": "energia",
            "valor_co2_kg": -5.0
        }
        response = client.post("/analisis", json=payload)
        assert response.status_code == 422

    def test_crear_analisis_co2_cero(self):
        payload = {
            "nombre": "Test cero",
            "categoria": "energia",
            "valor_co2_kg": 0.0
        }
        response = client.post("/analisis", json=payload)
        assert response.status_code == 422

    def test_crear_analisis_nombre_vacio(self):
        payload = {
            "nombre": "",
            "categoria": "energia",
            "valor_co2_kg": 10.0
        }
        response = client.post("/analisis", json=payload)
        assert response.status_code == 422

    def test_obtener_analisis_existente(self):
        payload = {
            "nombre": "Test obtener",
            "categoria": "transporte",
            "valor_co2_kg": 20.0
        }
        creado = client.post("/analisis", json=payload).json()
        response = client.get(f"/analisis/{creado['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == creado["id"]

    def test_obtener_analisis_no_existente(self):
        response = client.get("/analisis/99999")
        assert response.status_code == 404

    def test_listar_analisis_tras_crear(self):
        for i in range(3):
            client.post("/analisis", json={
                "nombre": f"Análisis {i}",
                "categoria": "energia",
                "valor_co2_kg": float(i + 1)
            })
        response = client.get("/analisis")
        assert len(response.json()) == 3

    def test_eliminar_analisis_existente(self):
        creado = client.post("/analisis", json={
            "nombre": "Borrar",
            "categoria": "agua",
            "valor_co2_kg": 1.0
        }).json()
        response = client.delete(f"/analisis/{creado['id']}")
        assert response.status_code == 200

    def test_eliminar_analisis_no_aparece_despues(self):
        creado = client.post("/analisis", json={
            "nombre": "Borrar check",
            "categoria": "agua",
            "valor_co2_kg": 1.0
        }).json()
        client.delete(f"/analisis/{creado['id']}")
        assert client.get(f"/analisis/{creado['id']}").status_code == 404

    def test_eliminar_analisis_no_existente(self):
        response = client.delete("/analisis/99999")
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════
# PRUEBAS DE INTEGRACIÓN — Estadísticas
# ═══════════════════════════════════════════════════════════

class TestEstadisticas:

    def setup_method(self):
        analisis_db.clear()

    def test_estadisticas_sin_datos(self):
        response = client.get("/estadisticas")
        assert response.status_code == 200
        assert response.json()["total_analisis"] == 0

    def test_estadisticas_co2_total(self):
        client.post("/analisis", json={
            "nombre": "A", "categoria": "energia", "valor_co2_kg": 10.0})
        client.post("/analisis", json={
            "nombre": "B", "categoria": "transporte", "valor_co2_kg": 20.0})
        data = client.get("/estadisticas").json()
        assert data["co2_total_kg"] == 30.0

    def test_estadisticas_promedio(self):
        client.post("/analisis", json={
            "nombre": "A", "categoria": "energia", "valor_co2_kg": 10.0})
        client.post("/analisis", json={
            "nombre": "B", "categoria": "energia", "valor_co2_kg": 30.0})
        data = client.get("/estadisticas").json()
        assert data["co2_promedio_kg"] == 20.0

    def test_estadisticas_maximo_minimo(self):
        client.post("/analisis", json={
            "nombre": "A", "categoria": "agua", "valor_co2_kg": 5.0})
        client.post("/analisis", json={
            "nombre": "B", "categoria": "agua", "valor_co2_kg": 100.0})
        data = client.get("/estadisticas").json()
        assert data["co2_maximo_kg"] == 100.0
        assert data["co2_minimo_kg"] == 5.0

    def test_estadisticas_por_categoria(self):
        client.post("/analisis", json={
            "nombre": "A", "categoria": "energia", "valor_co2_kg": 15.0})
        client.post("/analisis", json={
            "nombre": "B", "categoria": "transporte", "valor_co2_kg": 25.0})
        data = client.get("/estadisticas").json()
        assert "energia" in data["por_categoria"]
        assert "transporte" in data["por_categoria"]

    def test_estadisticas_por_nivel_impacto(self):
        client.post("/analisis", json={
            "nombre": "Bajo", "categoria": "agua", "valor_co2_kg": 5.0})
        client.post("/analisis", json={
            "nombre": "Critico", "categoria": "energia", "valor_co2_kg": 300.0})
        data = client.get("/estadisticas").json()
        assert "bajo" in data["por_nivel_impacto"]
        assert "critico" in data["por_nivel_impacto"]

    def test_estadisticas_total_analisis(self):
        for i in range(5):
            client.post("/analisis", json={
                "nombre": f"Test {i}",
                "categoria": "residuos",
                "valor_co2_kg": float(i + 1)
            })
        data = client.get("/estadisticas").json()
        assert data["total_analisis"] == 5
