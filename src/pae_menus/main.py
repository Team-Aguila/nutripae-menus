# pae_menus/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from pae_menus.database import init_db, close_db_connection, health_check as db_health_check
from pae_menus.api.ingredients import router as ingredients_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db_connection()


app = FastAPI(
    title="API de menús del PAE",
    description="Manejo de ingredientes, platos, menús, ciclos de menú y consulta pública.",
    version="1.0.0",
    lifespan=lifespan
)

# Include ingredient management routes
app.include_router(ingredients_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the PAE Coverage API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "PAE Menus API"}

@app.get("/health/database")
async def database_health_check():
    """Check database connection health"""
    return await db_health_check()
