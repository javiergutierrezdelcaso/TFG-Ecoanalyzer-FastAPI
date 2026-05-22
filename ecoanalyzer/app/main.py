from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import datetime

app = FastAPI()

# Montar carpeta /static
app.mount("/static", StaticFiles(directory="static"), name="static")

start_time = datetime.datetime.utcnow()

@app.get("/", response_class=HTMLResponse)
def home():
    environment = os.getenv("ENVIRONMENT", "unknown")
    version = os.getenv("IMAGE_TAG", "latest")
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    uptime = datetime.datetime.utcnow() - start_time

    return f"""
    <html>
        <head>
            <title>EcoAnalyzer — Dashboard</title>
            <link rel="stylesheet" href="/static/styles.css">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="/static/dashboard.js" defer></script>
        </head>

        <body>
            <div class="container fade-in">
                <img src="/static/logo.svg" class="logo" />

                <h1>EcoAnalyzer</h1>
                <h2>Microservicio desplegado correctamente en Azure</h2>

                <div class="cards">
                    <div class="card fade-in">
                        <div class="label">Entorno</div>
                        <div class="value">{environment}</div>
                    </div>

                    <div class="card fade-in">
                        <div class="label">Versión</div>
                        <div class="value">{version}</div>
                    </div>

                    <div class="card fade-in">
                        <div class="label">Último despliegue</div>
                        <div class="value">{timestamp}</div>
                    </div>

                    <div class="card fade-in">
                        <div class="label">Tiempo activo</div>
                        <div class="value">{str(uptime).split('.')[0]}</div>
                    </div>
                </div>

                <canvas id="chart" width="400" height="200"></canvas>

                <a class="btn" href="/docs">Ver documentación de la API</a>

                <footer>
                    EcoAnalyzer © {datetime.datetime.utcnow().year} — Proyecto TFG
                </footer>
            </div>
        </body>
    </html>
    """
