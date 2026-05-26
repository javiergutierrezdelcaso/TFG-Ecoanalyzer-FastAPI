from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime

app = FastAPI(
    title="Microservicio TFG",
    description="Microservicio de ejemplo desplegado con GitHub Actions y Terraform",
    version="1.0.0"
)


# ─────────────────────────────────────────────
# Modelos
# ─────────────────────────────────────────────
class Item(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float


class ItemResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    creado_en: str


# Base de datos en memoria (suficiente para el TFG)
items_db: dict[int, ItemResponse] = {}
contador_id = 1


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Health check — usado por las pruebas de integración del pipeline CD"""
    return {"status": "ok", "servicio": "microservicio-tfg", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    """Health check detallado"""
    return {
        "status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }


@app.get("/items", tags=["Items"])
def listar_items():
    """Devuelve todos los items"""
    return list(items_db.values())


@app.get("/items/{item_id}", tags=["Items"])
def obtener_item(item_id: int):
    """Devuelve un item por ID"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return items_db[item_id]


@app.post("/items", status_code=201, tags=["Items"])
def crear_item(item: Item):
    """Crea un nuevo item"""
    global contador_id
    nuevo = ItemResponse(
        id=contador_id,
        nombre=item.nombre,
        descripcion=item.descripcion,
        precio=item.precio,
        creado_en=datetime.datetime.utcnow().isoformat()
    )
    items_db[contador_id] = nuevo
    contador_id += 1
    return nuevo


@app.delete("/items/{item_id}", tags=["Items"])
def eliminar_item(item_id: int):
    """Elimina un item por ID"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    del items_db[item_id]
    return {"mensaje": f"Item {item_id} eliminado"}
