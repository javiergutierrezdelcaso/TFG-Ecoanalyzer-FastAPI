FROM python:3.10-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade \
    pip==25.2 \
    setuptools==80.9.0

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir \
    wheel==0.46.2 \
    jaraco.context==6.1.0

COPY . .

EXPOSE 8000

CMD ["uvicorn", "ecoanalyzer.app.main:app", "--host", "0.0.0.0", "--port", "8000"]