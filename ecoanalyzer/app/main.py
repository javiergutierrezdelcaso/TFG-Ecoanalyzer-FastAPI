from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import datetime

app = FastAPI()

# Ruta absoluta del directorio actual
BASE_DIR = Path(__file__).resolve().parent

# Carpeta static
STATIC_DIR = BASE_DIR / "static"

# Crear carpeta static si no existe
STATIC_DIR.mkdir(exist_ok=True)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

start_time = datetime.datetime.utcnow()


# Endpoint principal
@app.get("/")
def root():
    return {
        "service": "EcoAnalyzer",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "version": os.getenv("IMAGE_TAG", "latest"),
    }


# Endpoint healthcheck
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# Endpoint de análisis
@app.get("/analysis")
def analysis():
    return {
        "co2": 42,
        "energy": 120,
        "efficiency": "good",
    }


# Dashboard HTML
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    environment = os.getenv("ENVIRONMENT", "unknown")
    version = os.getenv("IMAGE_TAG", "latest")

    timestamp = datetime.datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    uptime = datetime.datetime.utcnow() - start_time

    footer_year = datetime.datetime.utcnow().year

    return f"""
    <html>
        <head>
            <title>EcoAnalyzer — Dashboard</title>

            <link
                rel="stylesheet"
                href="/static/styles.css"
            >

            <script src="https://cdn.jsdelivr.net/npm/chart.js">
            </script>

            <script
                src="/static/dashboard.js"
                defer
            ></script>
        </head>

        <body>
            <div class="container fade-in">

                <img
                    src="/static/logo.svg"
                    class="logo"
                />

                <h1>EcoAnalyzer</h1>

                <h2>
                    Microservicio desplegado correctamente en Azure
                </h2>

                <div class="cards">

                    <div class="card fade-in">
                        <div class="label">Entorno</div>

                        <div class="value">
                            {environment}
                        </div>
                    </div>

                    <div class="card fade-in">
                        <div class="label">Versión</div>

                        <div class="value">
                            {version}
                        </div>
                    </div>

                    <div class="card fade-in">
                        <div class="label">
                            Último despliegue
                        </div>

                        <div class="value">
                            {timestamp}
                        </div>
                    </div>

                    <div class="card fade-in">
                        <div class="label">
                            Tiempo activo
                        </div>

                        <div class="value">
                            {str(uptime).split(".")[0]}
                        </div>
                    </div>

                </div>

                <canvas
                    id="chart"
                    width="400"
                    height="200"
                ></canvas>

                <a class="btn" href="/docs">
                    Ver documentación de la API
                </a>

                <footer>
                    EcoAnalyzer © {footer_year}
                    — Proyecto TFG
                </footer>

            </div>
        </body>
    </html>
    """