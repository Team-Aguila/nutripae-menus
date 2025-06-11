# pae_menus/main.py
from fastapi import FastAPI

app = FastAPI(
    title="API de menús del PAE",
    description="Sistema para gestionar la estructura geográfica y de beneficiarios del PAE.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the PAE Coverage API"}
