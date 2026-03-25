# app/main.py

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import products, cart, orders, coupons


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Création des tables au démarrage
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ShopFlow API",
    lifespan=lifespan
)


# CORS (autorise tout pour dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(coupons.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}