import datetime
import os
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

KEY_VAULT_URI = os.getenv("KEY_VAULT_URI", "")
APP_SECRET = "no-configurado"


app = FastAPI(
    title="EcoAnalyzer API",
    description="Servicio de análisis de huella de carbono y consumo energético",
    version="1.0.0",
)

ENTORNO = os.getenv("ENTORNO", "PRE")
KEY_VAULT_URI = os.getenv("KEY_VAULT_URI", "")
APP_SECRET = "no-configurado"
if KEY_VAULT_URI:
    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KEY_VAULT_URI, credential=credential)
        APP_SECRET = client.get_secret("eco-api-secret").value
    except Exception as e:
        APP_SECRET = f"error-al-leer-kv: {e}"

# ─────────────────────────────────────────────
# Modelos
# ─────────────────────────────────────────────


class Analisis(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    categoria: str = Field(
        ..., description="energia | transporte | residuos | agua"
    )
    valor_co2_kg: float = Field(..., gt=0)
    descripcion: Optional[str] = None


class AnalisisResponse(BaseModel):
    id: int
    nombre: str
    categoria: str
    valor_co2_kg: float
    descripcion: Optional[str]
    nivel_impacto: str
    creado_en: str


CATEGORIAS_VALIDAS = {"energia", "transporte", "residuos", "agua"}

analisis_db: dict[int, AnalisisResponse] = {}
contador_id = 1


def calcular_nivel_impacto(co2_kg: float) -> str:
    if co2_kg < 10:
        return "bajo"
    elif co2_kg < 50:
        return "medio"
    elif co2_kg < 200:
        return "alto"
    else:
        return "critico"


# ─────────────────────────────────────────────
# Landing page visual
# ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, tags=["Info"])
def landing():
    total = len(analisis_db)
    co2_total = sum(a.valor_co2_kg for a in analisis_db.values())
    ahora = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S UTC")
    color_entorno = "#2ecc71" if ENTORNO == "PRO" else "#f39c12"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EcoAnalyzer</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
                max-width: 800px;
            }}
            .logo {{ font-size: 5rem; margin-bottom: 0.5rem; }}
            h1 {{
                font-size: 3rem;
                font-weight: 700;
                background: linear-gradient(90deg, #2ecc71, #1abc9c);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }}
            .tagline {{
                font-size: 1.1rem;
                color: #a0b4c0;
                margin-bottom: 2rem;
            }}
            .badge-entorno {{
                display: inline-block;
                background: {color_entorno};
                color: white;
                padding: 0.3rem 1rem;
                border-radius: 999px;
                font-weight: 600;
                font-size: 0.9rem;
                margin-bottom: 2rem;
                letter-spacing: 1px;
            }}
            .status {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background: rgba(46,204,113,0.15);
                border: 1px solid #2ecc71;
                border-radius: 999px;
                padding: 0.4rem 1.2rem;
                font-size: 0.95rem;
                margin-bottom: 2.5rem;
            }}
            .dot {{
                width: 10px; height: 10px;
                background: #2ecc71;
                border-radius: 50%;
                animation: pulse 1.5s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.3; }}
            }}
            .cards {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1rem;
                margin-bottom: 2rem;
            }}
            .card {{
                background: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 1.2rem;
            }}
            .card-value {{
                font-size: 2rem;
                font-weight: 700;
                color: #2ecc71;
            }}
            .card-label {{
                font-size: 0.8rem;
                color: #a0b4c0;
                margin-top: 0.2rem;
            }}
            .links {{
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            }}
            .link-btn {{
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                color: white;
                padding: 0.6rem 1.4rem;
                border-radius: 8px;
                text-decoration: none;
                font-size: 0.9rem;
                transition: background 0.2s;
            }}
            .link-btn:hover {{ background: rgba(255,255,255,0.2); }}
            .footer {{
                margin-top: 2.5rem;
                font-size: 0.75rem;
                color: #5a7080;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🌿</div>
            <h1>EcoAnalyzer</h1>
            <p class="tagline">
                Análisis de huella de carbono y consumo energético
            </p>
            <div class="badge-entorno">ENTORNO: {ENTORNO}</div>
            <br>
            <div class="status">
                <div class="dot"></div>
                Servicio operativo
            </div>
            <div class="cards">
                <div class="card">
                    <div class="card-value">{total}</div>
                    <div class="card-label">Análisis registrados</div>
                </div>
                <div class="card">
                    <div class="card-value">{co2_total:.1f}</div>
                    <div class="card-label">kg CO₂ analizados</div>
                </div>
                <div class="card">
                    <div class="card-value">v1.0</div>
                    <div class="card-label">Versión del servicio</div>
                </div>
            </div>
            <div class="links">
                <a class="link-btn" href="/docs">📖 Documentación API</a>
                <a class="link-btn" href="/health">❤️ Health Check</a>
                <a class="link-btn" href="/analisis">📊 Análisis</a>
                <a class="link-btn" href="/estadisticas">📈 Estadísticas</a>
                <a class="link-btn" href="/categorias">🏷️ Categorías</a>
            </div>
            <div class="footer">
                Última comprobación: {ahora} ·
                TFG — Automatización de Despliegue con GitHub Actions y Terraform
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "servicio": "ecoanalyzer",
        "version": "1.0.0",
        "entorno": ENTORNO,
        "kv_conectado": KEY_VAULT_URI != "",
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# Categorías
# ─────────────────────────────────────────────
@app.get("/categorias", tags=["Categorías"])
def listar_categorias():
    return {
        "categorias": [
            {
                "id": "energia",
                "nombre": "Energía",
                "descripcion": "Consumo eléctrico y combustibles",
            },
            {
                "id": "transporte",
                "nombre": "Transporte",
                "descripcion": "Emisiones por desplazamiento",
            },
            {
                "id": "residuos",
                "nombre": "Residuos",
                "descripcion": "Generación y gestión de residuos",
            },
            {
                "id": "agua",
                "nombre": "Agua",
                "descripcion": "Consumo y tratamiento de agua",
            },
        ]
    }


# ─────────────────────────────────────────────
# CRUD Análisis
# ─────────────────────────────────────────────
@app.get("/analisis", tags=["Análisis"])
def listar_analisis():
    return list(analisis_db.values())


@app.get("/analisis/{analisis_id}", tags=["Análisis"])
def obtener_analisis(analisis_id: int):
    if analisis_id not in analisis_db:
        raise HTTPException(
            status_code=404, detail=f"Análisis {analisis_id} no encontrado"
        )
    return analisis_db[analisis_id]


@app.post("/analisis", status_code=201, tags=["Análisis"])
def crear_analisis(analisis: Analisis):
    global contador_id
    if analisis.categoria not in CATEGORIAS_VALIDAS:
        raise HTTPException(
            status_code=422,
            detail=f"Categoría inválida. Válidas: {CATEGORIAS_VALIDAS}",
        )
    nuevo = AnalisisResponse(
        id=contador_id,
        nombre=analisis.nombre,
        categoria=analisis.categoria,
        valor_co2_kg=analisis.valor_co2_kg,
        descripcion=analisis.descripcion,
        nivel_impacto=calcular_nivel_impacto(analisis.valor_co2_kg),
        creado_en=datetime.datetime.utcnow().isoformat(),
    )
    analisis_db[contador_id] = nuevo
    contador_id += 1
    return nuevo


@app.delete("/analisis/{analisis_id}", tags=["Análisis"])
def eliminar_analisis(analisis_id: int):
    if analisis_id not in analisis_db:
        raise HTTPException(
            status_code=404, detail=f"Análisis {analisis_id} no encontrado"
        )
    del analisis_db[analisis_id]
    return {"mensaje": f"Análisis {analisis_id} eliminado correctamente"}


# ─────────────────────────────────────────────
# Estadísticas
# ─────────────────────────────────────────────
@app.get("/estadisticas", tags=["Estadísticas"])
def obtener_estadisticas():
    if not analisis_db:
        return {
            "total_analisis": 0,
            "co2_total_kg": 0,
            "co2_promedio_kg": 0,
            "co2_maximo_kg": 0,
            "co2_minimo_kg": 0,
            "por_categoria": {},
            "por_nivel_impacto": {},
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
