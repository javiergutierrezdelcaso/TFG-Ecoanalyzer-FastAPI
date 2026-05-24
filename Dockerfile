# hadolint ignore=DL3008
FROM python:3.11-slim-trixie

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade \
    pip==25.2 \
    setuptools==80.9.0 \
    wheel==0.46.2 \
    jaraco.context==6.1.0 \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "ecoanalyzer.app:app", "--host", "0.0.0.0", "--port", "8000"]