# 🌿 EcoAnalyzer — Microservicio

Repositorio del microservicio **EcoAnalyzer**, desarrollado como Trabajo de Fin 
de Grado en Ingeniería Informática. Esta herramienta, bautizada como EcoAnalyzer, 
tiene como propósito evaluar el impacto energético y la huella de carbono. 
Para su construcción, se ha seleccionado el lenguaje **Python** en combinación 
con el framework **FastAPI**, desplegada automáticamente en **Microsoft Azure** 
mediante pipelines CI/CD con **GitHub Actions**.

---

## Funcionalidades

- **Landing page visual** con métricas en tiempo real y badge de entorno (PRE/PRO)
- **Gestión de análisis medioambientales** con cálculo automático del nivel de impacto
- **Estadísticas agregadas** de CO₂ por categoría y nivel de impacto
- **Categorías**: energía, transporte, residuos y agua
- **Health check** con información del entorno y versión

---

### Especificación de Endpoints de la API

| Verbo HTTP | Dirección del Recurso | Propósito y Respuesta del Servicio |
| :--- | :--- | :--- |
| **GET** | `/` | Renderizado de la interfaz gráfica principal (Página de inicio en HTML). |
| **GET** | `/health` | Diagnóstico del estado del sistema, incluyendo variables de entorno y marca de tiempo (*timestamp*). |
| **GET** | `/categorias` | Consulta del catálogo completo de clasificaciones disponibles en la plataforma. |
| **GET** | `/analisis` | Recuperación del histórico global de registros evaluados. |
| **GET** | `/analisis/{id}` | Extracción de un reporte específico utilizando su identificador único. |
| **GET** | `/estadisticas` | Cálculo de métricas consolidadas y datos acumulados sobre emisiones de CO₂. |
| **POST** | `/analisis` | Procesamiento e inserción de un nuevo estudio o registro en el sistema. |
| **DELETE** | `/analisis/{id}` | Remoción o purga de un registro específico de la base de datos mediante su ID. |

Documentación interactiva disponible en `/docs` (Swagger UI).

---

## Estructura del repositorio

```
microservicio/
├── main.py                         # Aplicación FastAPI — EcoAnalyzer
├── requirements.txt                # Dependencias Python
├── test_main.py                    # 57 pruebas automatizadas (pytest)
├── .gitignore
└── .github/
    ├── dependabot.yml              # Actualización automática de dependencias
    └── workflows/
        ├── ci.yml                  # Pipeline CI — validación en PRs
        ├── cd.yml                  # Pipeline CD — despliegue PRE y PRO
        └── codeql.yml              # Análisis de seguridad CodeQL
```

---

## Pipelines CI/CD

### CI — Validación de Pull Request (`ci.yml`)

Se dispara automáticamente al abrir una PR hacia `main`.

```
Checkout → Python 3.11 → Instalar deps → flake8 → pytest + cobertura ≥ 80%
```

El merge queda **bloqueado** si alguna validación falla.

### CD — Despliegue PRE y PRO (`cd.yml`)

Se dispara automáticamente al hacer merge a `main`.

```
validacion → despliegue-pre → pruebas-integracion → despliegue-pro
                                                     (aprobación humana)
```

| Job | Descripción |
|---|---|
| `validacion` | Repite las validaciones de CI |
| `despliegue-pre` | Obtiene IP de Azure, despliega en PRE via SSH |
| `pruebas-integracion` | Health check, landing page, categorías, análisis, estadísticas |
| `despliegue-pro` | Aprobación humana + despliegue en PRO + health check |

La IP de las VMs se obtiene automáticamente desde **Azure CLI** 
sin necesidad de configurar ninguna variable manual.

### CodeQL — Análisis de seguridad (`codeql.yml`)

Ejecuta análisis estático de seguridad sobre el código Python en cada PR, 
push a main y automáticamente cada lunes. Los resultados aparecen en 
**Security → Code scanning alerts**.

---

## Pruebas

57 pruebas organizadas en 5 clases cubriendo los tres niveles de la pirámide:

| Clase | Tipo | Nº pruebas | Descripción |
|---|---|---|---|
| `TestCalcularNivelImpacto` | Unitaria | 12 | Función de cálculo de impacto con valores límite |
| `TestHealthYLanding` | Integración | 8 | Endpoints de estado y landing page |
| `TestCategorias` | Integración | 7 | Endpoint de categorías |
| `TestAnalisisCRUD` | Integración | 16 | CRUD completo con casos límite |
| `TestEstadisticas` | Integración | 7 | Cálculos de estadísticas agregadas |

Ejecutar en local:
```bash
pip install -r requirements.txt
pytest test_main.py -v --cov=main --cov-report=term-missing
```

---

## Secretos y variables necesarios

### Repository secrets

| Secret | Descripción |
|---|---|
| `SSH_PRIVATE_KEY` | Clave privada RSA para conectar a las VMs |
| `AZURE_CREDENTIALS1` | JSON con credenciales del Service Principal de Azure |

### Repository variables

| Variable | Descripción |
|---|---|
| `TF_ORGANIZATION` | Nombre de la organización en Terraform Cloud |

### Entorno `pre` (GitHub Environments)

No requiere variables adicionales. La IP se obtiene automáticamente desde Azure.

### Entorno `pro` (GitHub Environments)

Configurar **Required reviewers** con tu usuario para activar la aprobación 
humana antes del despliegue en producción.

---

## Desarrollo local

### Requisitos
- Python 3.10+
- pip

### Instalación
```bash
git clone https://github.com/TU_USUARIO/microservicio.git
cd microservicio
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Arrancar el servicio
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Abre [http://localhost:8000](http://localhost:8000) para ver la landing page.

### Ejecutar pruebas
```bash
pytest test_main.py -v --cov=main --cov-report=term-missing
```

---

## Modelo de datos

### Análisis (POST /analisis)

```json
{
  "nombre": "Consumo oficina mensual",
  "categoria": "energia",
  "valor_co2_kg": 45.5,
  "descripcion": "Consumo eléctrico de la oficina durante marzo"
}
```

Categorías válidas: `energia`, `transporte`, `residuos`, `agua`

### Niveles de impacto (calculados automáticamente)

| Nivel | Rango CO₂ |
|---|---|
| `bajo` | < 10 kg |
| `medio` | 10 – 49.99 kg |
| `alto` | 50 – 199.99 kg |
| `critico` | ≥ 200 kg |

---

## Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs)
- [pytest Documentation](https://docs.pytest.org)
