# app/main.py
"""
Entry point for the FastAPI app. Loads ontology and mounts routes.
"""

from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI(title="Strings to Things")

app.include_router(router)
