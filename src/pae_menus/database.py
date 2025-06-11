# pae_cobertura/database.py
from sqlmodel import create_engine

from pae_cobertura.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)
