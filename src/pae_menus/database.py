# pae_menus/database.py
from sqlmodel import create_engine

from pae_menus.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)
