FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements desde ecoanalyzer
COPY ecoanalyzer/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del microservicio
COPY ecoanalyzer/ .

# Copiar carpeta de archivos estáticos (CSS, JS, imágenes)
COPY ecoanalyzer/static /app/static

# Exponer puerto FastAPI
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
