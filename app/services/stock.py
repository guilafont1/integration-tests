import logging

from sqlalchemy.orm import Session

from app.cache import redis_client
from app.models import Product

logger = logging.getLogger(__name__)


def verifier_stock(product: Product, quantite: int) -> bool:
    if quantite <= 0:
        raise ValueError(f"Quantité invalide : {quantite}")

    return product.stock >= quantite


def reserver_stock(
    product: Product, quantite: int, session: Session
) -> Product:
    if not verifier_stock(product, quantite):
        raise ValueError(
            f"Stock insuffisant pour '{product.name}' : "
            f"{product.stock} disponible(s), {quantite} demandé(s)."
        )

    product.stock -= quantite
    session.commit()
    session.refresh(product)

    cache_key = f"product:{product.id}:stock"
    redis_client.delete(cache_key)
    logger.info("Stock réservé : %s, qty=%s", product.id, quantite)
    return product


def liberer_stock(
    product: Product, quantite: int, session: Session
) -> Product:
    if quantite <= 0:
        raise ValueError(f"Quantité invalide : {quantite}")

    product.stock += quantite
    session.commit()
    session.refresh(product)

    redis_client.set(f"product:{product.id}:stock", product.stock)
    return product
