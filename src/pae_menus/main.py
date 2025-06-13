# pae_menus/main.py
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from .core.config import settings
from .api import api_router
from .models import Ingredient, Dish, MenuCycle, MenuSchedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    """
    logger.info("Starting up...")
    app.mongodb_client = AsyncIOMotorClient(settings.mongo_url)
    app.mongodb = app.mongodb_client[settings.mongo_db_name]

    await init_beanie(
        database=app.mongodb,
        document_models=[
            Ingredient,
            Dish,
            MenuCycle,
            MenuSchedule,
        ]
    )
    logger.info("Database and Beanie initialized.")
    
    yield
    
    logger.info("Shutting down...")
    app.mongodb_client.close()
    logger.info("MongoDB connection closed.")


app = FastAPI(
    title="API de menús del PAE",
    description="Manejo de ingredientes, platos, menús, ciclos de menú y consulta pública.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the PAE Menus API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "PAE Menus API"}

@app.get("/health/database")
async def database_health_check():
    """Check database connection health"""
    try:
        # Simple database connection test
        await app.mongodb.list_collection_names()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
