import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import Engine

from app.database import Base, engine as default_engine
from app.routes import cart, coupons, orders, products

logging.basicConfig(level=logging.INFO)


def create_app(engine: Optional[Engine] = None) -> FastAPI:
    db_engine = engine or default_engine

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(bind=db_engine)
        yield

    app = FastAPI(title="ShopFlow API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(products.router)
    app.include_router(cart.router)
    app.include_router(orders.router)
    app.include_router(coupons.router)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()
