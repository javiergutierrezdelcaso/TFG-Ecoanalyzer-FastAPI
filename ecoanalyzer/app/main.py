from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import datetime
import random
from typing import Optional

app = FastAPI(
    title="EcoAnalyzer API",
    description="Microservicio de análisis de eficiencia energética",
    version="2.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

start_time = datetime.datetime.utcnow()

# Almacén de análisis (simulado)
analysis_history = []


@app.get("/")
def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "ecoanalyzer",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "version": os.getenv("IMAGE_TAG", "latest"),
        "uptime_seconds": (datetime.datetime.utcnow() - start_time).total_seconds(),
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}


@app.get("/analysis")
def analysis(endpoint: Optional[str] = None):
    """
    Endpoint de análisis con parámetro opcional
    
    Args:
        endpoint: Parámetro opcional para filtrar análisis
    """
    result = {
        "co2": 42,
        "energy": 120,
        "efficiency": "good",
        "temperature": 22.5,
        "humidity": 45,
    }
    
    analysis_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "result": result,
        "endpoint": endpoint or "default",
    }
    
    analysis_history.append(analysis_entry)
    
    return analysis_entry


@app.get("/analysis/history")
def get_analysis_history(limit: int = 10):
    """Obtener historial de análisis"""
    return {
        "total": len(analysis_history),
        "analyses": analysis_history[-limit:],
    }


@app.get("/analysis/stats")
def get_analysis_stats():
    """Obtener estadísticas de análisis"""
    if not analysis_history:
        return {"message": "No hay análisis disponibles", "total": 0}
    
    total_co2 = sum(a["result"]["co2"] for a in analysis_history)
    total_energy = sum(a["result"]["energy"] for a in analysis_history)
    
    return {
        "total_analyses": len(analysis_history),
        "total_co2": total_co2,
        "total_energy": total_energy,
        "average_co2": total_co2 / len(analysis_history),
        "average_energy": total_energy / len(analysis_history),
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Dashboard visual mejorado"""
    environment = os.getenv("ENVIRONMENT", "unknown")
    version = os.getenv("IMAGE_TAG", "latest")
    
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    uptime = datetime.datetime.utcnow() - start_time
    footer_year = datetime.datetime.utcnow().year
    
    # Datos simulados para el gráfico
    chart_data = [random.randint(30, 70) for _ in range(12)]
    chart_data_json = str(chart_data).replace("'", '"')
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EcoAnalyzer Dashboard</title>
            <link rel="stylesheet" href="/static/styles.css">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 2em; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1 {{ color: #667eea; margin: 0.5em 0; }}
                h2 {{ color: #764ba2; margin-top: 0; }}
                .info {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1em; margin: 2em 0; }}
                .info-card {{ background: #f5f5f5; padding: 1em; border-radius: 5px; border-left: 4px solid #667eea; }}
                .info-card strong {{ color: #667eea; }}
                canvas {{ margin: 2em 0; }}
                footer {{ text-align: center; margin-top: 2em; color: #888; font-size: 0.9em; border-top: 1px solid #ddd; padding-top: 1em; }}
                .fade-in {{ animation: fadeIn 0.5s; }}
                @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            </style>
        </head>
        <body>
            <div class="container fade-in">
                <h1>🌱 EcoAnalyzer</h1>
                <h2>Microservicio desplegado correctamente en Azure</h2>
                
                <div class="info">
                    <div class="info-card">
                        <strong>Entorno:</strong> {environment}
                    </div>
                    <div class="info-card">
                        <strong>Versión:</strong> {version}
                    </div>
                    <div class="info-card">
                        <strong>Uptime:</strong> {uptime}
                    </div>
                    <div class="info-card">
                        <strong>Timestamp:</strong> {timestamp}
                    </div>
                </div>
                
                <div style="background: #f9f9f9; padding: 1.5em; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #667eea;">📊 Consumo CO₂ Mensual Simulado</h3>
                    <canvas id="ecoChart"></canvas>
                </div>
            </div>
            
            <footer>&copy; {footer_year} EcoAnalyzer - Análisis de Eficiencia Energética</footer>
            
            <script>
                const ctx = document.getElementById('ecoChart').getContext('2d');
                const chartData = {chart_data_json};
                
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                        datasets: [{{
                            label: 'CO₂ (kg)',
                            data: chartData,
                            borderColor: 'rgba(102, 126, 234, 1)',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 5,
                            pointHoverRadius: 7
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{ 
                                display: true,
                                labels: {{ color: '#333', font: {{ size: 12 }} }}
                            }},
                            title: {{ 
                                display: true,
                                text: 'Proyección CO₂ Mensual',
                                color: '#333',
                                font: {{ size: 14 }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100,
                                ticks: {{ color: '#666' }},
                                grid: {{ color: 'rgba(200, 200, 200, 0.2)' }}
                            }},
                            x: {{
                                ticks: {{ color: '#666' }},
                                grid: {{ color: 'rgba(200, 200, 200, 0.2)' }}
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
    </html>
    """