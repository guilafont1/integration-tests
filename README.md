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

### JUnit XML (TP2)

Générer un rapport JUnit XML (utile pour CI / Sonar / Jenkins) :

```bash
python -m pytest --junitxml=report.xml
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

## CI Pipeline (TP3)

Le projet inclut un pipeline reproductible qui valide automatiquement :

- **Lint** : `flake8`
- **Tests** : `pytest` (en parallèle via `pytest-xdist`, `-n auto`)
- **Coverage gate** : seuil `--cov-fail-under=80` (config dans `pytest.ini`)

Exécution du pipeline (Windows / PowerShell) :

```bash
powershell -ExecutionPolicy Bypass -File run_pipeline.ps1
```

## TP4 (qualité avancée)

- **E2E** : `tests/integration/test_e2e_flow.py` (flow complet produit → panier → commande)
- **Sécurité** : `bandit -r app` (intégré au pipeline `run_pipeline.ps1`)
- **Performance** : `locustfile.py` (lancer `locust` puis ouvrir `http://localhost:8089`)
- **TDD (coupon)** : exemple de règle métier “réduction max 30%” + tests (`tests/unit/test_coupon.py`)

### TP4 — Rapport performance (Locust)

Pré-requis : lancer l’API en local.

```bash
uvicorn app.main:app --reload
```

Lancer Locust :

```bash
locust --host http://127.0.0.1:8000
```

#### Générer automatiquement un rapport HTML (TP4)

Le script `run_locust.ps1` génère un rapport **HTML** et des **CSV** dans `reports/` :

```bash
powershell -ExecutionPolicy Bypass -File run_locust.ps1
```

Variables d’environnement optionnelles :

- `LOCUST_HOST` (défaut: `http://127.0.0.1:8000`)
- `LOCUST_USERS` (défaut: 50)
- `LOCUST_SPAWN_RATE` (défaut: 2)
- `LOCUST_RUN_TIME` (défaut: 1m)

Puis ouvrir `http://localhost:8089` et exécuter un test (ex : 50 users).

#### Résultats (exemple de campagne)

- **Charge** : 50 utilisateurs concurrents
- **Débit** : ~69 req/s
- **Temps moyen** : ~55–57 ms
- **Percentiles** :
  - P95 ~230–270 ms
  - P99 ~430–740 ms
- **Max latency** : ~1135 ms (pics ponctuels)
- **Failures** : 0%

#### Conclusion

L’API reste **stable** sous charge concurrente modérée, avec une **augmentation progressive** de la latence (attendue, notamment avec SQLite et sans cache distribué).

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

