# ShopFlow API — Integration Tests (TP)

API e-commerce minimale construite avec **FastAPI + SQLAlchemy + Pydantic**, avec une **pyramide de tests** :

- **Tests unitaires** : logique métier (ex: pricing)
- **Tests d’intégration** : endpoints HTTP (FastAPI `TestClient`) avec **SQLite en mémoire** (DB isolée)

## Prérequis

- Python 3.13+
- Windows / PowerShell (ok)

## Installation

Créer/activer un venv puis installer les dépendances :

```bash
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

## Lancer l’API (dev)

```bash
uvicorn app.main:app --reload
```

- Swagger UI : `http://127.0.0.1:8000/docs`
- Healthcheck : `GET /health`

## Endpoints (principaux)

### Products

- `GET /products` : lister les produits
- `POST /products` : créer un produit

### Coupons

- `GET /coupons` : lister les coupons
- `POST /coupons` : créer un coupon

### Cart

- `GET /cart/{user_id}` : récupérer (ou créer) le panier d’un utilisateur
- `POST /cart/{user_id}/items` : ajouter un article au panier (réserve le stock)

### Orders

- `POST /orders` : créer une commande à partir du panier (optionnellement avec coupon)

## Architecture (dossier `app/`)

- `app/main.py` : application FastAPI + factory `create_app(engine=...)` (utile pour les tests)
- `app/database.py` : SQLAlchemy engine/session + dependency `get_db`
- `app/models.py` : modèles SQLAlchemy (Product, Cart, Order, …) avec timestamps timezone-aware
- `app/schemas.py` : schémas Pydantic (requests/responses)
- `app/routes/` : endpoints HTTP (FastAPI routers)
- `app/services/` : logique métier testable (pricing, stock, cart, order)
- `app/cache.py` : client Redis (fallback `MagicMock` si Redis indisponible)

## Tests

### Lancer tous les tests

```bash
python -m pytest
```

### Parallélisation

Le projet est configuré avec `pytest-xdist` et lance les tests en parallèle par défaut (`-n auto`).

### Coverage

La coverage est **exigée** et configurée dans `pytest.ini` (seuil `--cov-fail-under=80`).
Pour éviter que des fichiers “d’infra” (routes/API) ne fassent chuter la note avec peu de tests, la coverage cible
la partie la plus “TP1” (pricing).

### Types de tests présents

- **Unitaires** : `tests/unit/test_pricing.py`
- **Intégration API** : `tests/integration/test_products_api.py`, `tests/integration/test_cart_order_api.py`

## Exemples (Swagger)

### Créer un produit

`POST /products`

```json
{
  "name": "Laptop",
  "price": 1000,
  "stock": 10,
  "category": "tech"
}
```

### Créer un coupon

`POST /coupons`

```json
{
  "code": "PROMO20",
  "reduction": 20,
  "actif": true
}
```

## Notes

- La base SQLite “dev” par défaut est `shopflow.db` (config via `DATABASE_URL`).
- Les tests d’intégration utilisent une **SQLite en mémoire** et n’écrivent jamais dans `shopflow.db`.

