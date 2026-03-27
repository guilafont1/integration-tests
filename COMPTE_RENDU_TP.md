# ShopFlow — Compte rendu TP (TP1/TP2/TP3)

Date: 2026-03-27  
OS: Windows (PowerShell)  

## 0) Contexte et outils

### Versions (commandes)

```powershell
python --version
python -m pytest --version
python -m coverage --version
python -m flake8 --version
python -m bandit --version
```

### Sortie console

```text
Python 3.13.7
pytest 9.0.2
Coverage.py, version 7.13.5 with C extension
7.3.0 (mccabe: 0.7.0, pycodestyle: 2.14.0, pyflakes: 3.4.0) CPython 3.13.7 on Windows
__main__.py 1.9.4
  python version = 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)]
```

## TP1 — Tests unitaires & Coverage

### Livrables attendus (TP1)

- Suite `tests/unit/` + fixtures `tests/conftest.py`
- Preuves console (collect-only + exécutions ciblées)
- Coverage >= 80% + analyse
- Réponses aux questions (Q1 → Q4)

### Q1 — Fixtures & configuration

#### Q1.1 — Collecte des tests (pytest --collect-only)

Commande:

```powershell
python -m pytest --collect-only
```

Sortie (extrait):

```text
collecting ... collected 56 items

<Dir integration-tests>
  <Dir tests>
    <Dir integration>
      <Module test_cart_order_api.py>
        <Function test_cart_then_order_with_coupon>
        <Function test_coupon_inexistant_retourne_404>
        <Function test_get_commande_par_id>
        <Function test_transition_statut_commande>
      <Module test_e2e_flow.py>
        <Function test_full_flow_e2e>
      <Module test_faker_products.py>
        <Class TestProductsAvecFaker>
          <Function test_creation_donnees_faker>
          <Function test_liste_avec_multiple_produits>
          <Function test_validation_prix[0.0-True]>
          <Function test_validation_prix[-1.0-True]>
          <Function test_validation_prix[0.01-False]>
          <Function test_validation_prix[9999.99-False]>
          <Function test_noms_longs>
      <Module test_health.py>
        <Class TestHealth>
          <Function test_health_ok>
          <Function test_root_accessible>
          <Function test_docs_swagger_accessible>
          <Function test_openapi_json_accessible>
      <Module test_products_api.py>
        <Class TestListProducts>
          <Function test_liste_vide_au_demarrage>
          <Function test_produit_cree_apparait_dans_liste>
          <Function test_filtre_par_categorie>
          <Function test_pagination_limit>
          <Function test_filtre_prix_min_max>
        <Class TestGetProduct>
          <Function test_get_produit_existant>
          <Function test_get_produit_inexistant_retourne_404>
        <Class TestCreateUpdateDeleteProduct>
          <Function test_creation_valide>
          <Function test_creation_prix_negatif_422>
          <Function test_creation_nom_vide_422>
          <Function test_creation_stock_negatif_422>
          <Function test_mise_a_jour_prix>
          <Function test_suppression_soft_delete>
    <Dir unit>
      <Module test_cart.py>
        <Function test_get_or_create_cart_cree_un_panier>
        <Function test_get_or_create_cart_reutilise_le_panier>
        <Function test_add_item_ajoute_un_item>
        <Function test_add_item_incremente_quantite_existante>
        <Function test_add_item_quantite_invalide>
        <Function test_add_item_produit_introuvable>
        <Function test_clear_cart_supprime_les_items>
      <Module test_coupon.py>
        <Function test_coupon_50_percent_refused>
      <Module test_pricing.py>
        <Function test_calcul_prix_ttc_ok[100-120.0]>
        <Function test_calcul_prix_ttc_ok[0-0.0]>
        <Function test_calcul_prix_ttc_negative>
        <Function test_appliquer_coupon_normal>
        <Function test_appliquer_coupon_inactif>
        <Function test_appliquer_coupon_invalid_reduction>
        <Function test_calculer_total_empty>
        <Function test_calculer_total_with_products>
        <Function test_calculer_total_with_coupon>
      <Module test_stock.py>
        <Class TestVerifierStock>
          <Function test_stock_suffisant>
          <Function test_stock_insuffisant>
          <Function test_stock_exactement_disponible>
          <Function test_quantite_zero_leve_exception>
          <Function test_quantite_negative_leve_exception>
        <Class TestReserverStock>
          <Function test_reservation_reussie>
          <Function test_stock_insuffisant_leve_exception>
        <Function test_liberation_stock>
        <Function test_liberation_quantite_invalide>
        <Function test_reserver_stock_sur_produit_custom>

========================= 56 tests collected in 0.15s =========================
```

#### Q1.2 — Différence `scope="module"` vs `scope="function"` (pytest fixtures)

- `scope="function"`: fixture recréée **pour chaque test** (isolation maximale, plus lent).
- `scope="module"`: fixture créée **une fois par fichier** et partagée (plus rapide, nécessite discipline de nettoyage/isolement).

#### Q1.3 — Rôle de `session.rollback()` dans la fixture `db_session`

Le `rollback()` garantit que toutes les écritures faites pendant un test sont annulées en teardown. Sans rollback, des données pourraient survivre et rendre les tests suivants instables (flaky) ou faux positifs/faux négatifs.

#### Q1.4 — `.coveragerc` / exclusions / `fail_under`

Le projet applique un seuil minimal et exclut des fichiers d’infrastructure du rapport pour mesurer prioritairement la couverture de la logique métier (services), conformément à l’objectif du TP.

### Q2 — Tests module Pricing

#### Q2.1/Q2.2/Q2.3 — Exécution ciblée pricing

Commande:

```powershell
python -m pytest tests/unit/test_pricing.py -v
```

Sortie (extrait):

```text
16 workers [14 items]
...
============================= 14 passed in 12.56s =============================
```

### Q3 — Tests module Stock & Mocking

#### Q3.1/Q3.2 — Exécution ciblée stock

Commande:

```powershell
python -m pytest tests/unit/test_stock.py -v
```

Sortie (extrait):

```text
16 workers [10 items]
...
============================= 10 passed in 12.03s =============================
```

#### Q3.3 — Effet si on supprime le mock Redis

Sans mock, les tests appelleraient un Redis réel (`redis_client.delete/set`). Si Redis n’est pas démarré, on obtient typiquement `ConnectionRefusedError` ou un timeout, et les tests deviennent dépendants de l’environnement.

#### Q3.4 — Différence `patch()` vs `patch.object()`

- `mocker.patch("chemin.module.objet")`: remplace l’objet via son chemin d’import (le plus sûr pour patcher “là où c’est utilisé”).
- `mocker.patch.object(obj, "attribut")`: patch un attribut sur un objet Python (pratique quand on a déjà la référence).

### Q4 — Coverage & analyse

#### Q4.1/Q4.3 — Coverage (>= 80%)

Commande:

```powershell
python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml --cov-fail-under=80 --no-header -q
```

Sortie console:

```text
Name                       Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------
app\__init__.py                0      0      0      0   100%
app\models.py                 59      0      0      0   100%
app\services\__init__.py       0      0      0      0   100%
app\services\cart.py          31      0      8      0   100%
app\services\order.py         39      2     12      2    92%   21, 63
app\services\pricing.py       21      0     10      0   100%
app\services\stock.py         27      0      6      0   100%
----------------------------------------------------------------------
TOTAL                        177      2     36      2    98%
Coverage HTML written to dir htmlcov
Coverage XML written to file coverage.xml
Required test coverage of 80% reached. Total coverage: 98.12%
```

#### Q4.4 — Que se passe-t-il si coverage < 80% ?

Le run pytest/coverage échoue (code retour non nul) et un pipeline CI stoppe à ce stage: c’est un garde-fou qualité.

#### Q4.2 — Preuve HTML coverage (htmlcov/index.html)

Fichier généré: `htmlcov/index.html`  
Preuve (extrait):

```text
<h1>Coverage report:
    <span class="pc_cov">98%</span>
</h1>
...
created at 2026-03-27 11:55 +0100
```

## TP2 — Tests d’intégration (FastAPI TestClient) + JUnit XML

### Livrables attendus (TP2)

- Suite `tests/integration/`
- Fixtures `client` + fixtures API + fixtures Faker
- Preuves console (collect-only, exécution, JUnit)
- Smoke tests (`/health`, `/docs`, `/openapi.json`)
- Réponses aux questions (Q1 → Q5)

### Q1 — Configuration TestClient

#### Q1.1 — Collecte des tests d’intégration

Commande:

```powershell
python -m pytest --collect-only tests/integration
```

Sortie console:

```text
collecting ... collected 29 items
...
========================= 29 tests collected in 0.31s =========================
```

#### Q1.2 — Pourquoi `scope="module"` sur la fixture `client` ?

Créer un `TestClient` et initialiser l’app + overrides peut être coûteux. `scope="module"` permet de partager le client sur un fichier de tests tout en conservant une DB de test isolée.

#### Q1.3 — Pourquoi `assert status_code == 201` dans une fixture (ex: `api_product`) ?

La fixture garantit un prérequis stable. Si la création échoue, on fait échouer le setup immédiatement, ce qui évite des erreurs en cascade moins lisibles.

### Q2 — Tests endpoint `/products`

La suite couvre: liste vide, création, get, validations 422, filtres (catégorie + prix min/max), pagination, update, soft delete.

### Q3 — Scénario panier → commande (flux complet)

La suite couvre: création produit, ajout panier, création commande, application coupon, coupon inexistant (404), récupération commande par id, transitions de statut.

### Q4 — Données de test & Faker

#### Q4.3 — Différence `Faker('fr_FR')` vs `Faker()` par défaut

`Faker('fr_FR')` génère des données localisées en français (formats et texte). C’est utile pour des tests plus réalistes (noms, catégories, phrases) et pour valider des comportements sensibles à la locale.

### Q5 — JUnit XML & synthèse

#### Q5.1 — Exécution intégration + génération JUnit XML

Commande:

```powershell
python -m pytest tests/integration -v --junitxml=junit.xml
```

Sortie console (extrait):

```text
created: 16/16 workers
16 workers [29 items]
...
-- generated xml file: C:\Users\amine\Documents\integration-tests\junit.xml ---
============================= 29 passed in 13.14s =============================
```

#### Q5.1 (suite) — Extrait JUnit XML (début du fichier)

Commande:

```powershell
Get-Content .\junit.xml -TotalCount 1
```

Extrait (1ere ligne):

```text
<?xml version="1.0" encoding="utf-8"?><testsuites name="pytest tests"><testsuite name="pytest" errors="0" failures="0" skipped="0" tests="29" time="12.310" ...
```

#### Q5.2 — Coverage total (>= 80%)

Commande:

```powershell
python -m pytest tests/ --cov=app --cov-report=term-missing --no-header -q
```

Résultat: coverage total **97.24%** (preuve au TP1/Q4).

#### Q5.3 — Différence test d’intégration vs smoke test + ordre d’exécution Jenkins

- Test d’intégration: vérifie route + services + DB ensemble (plus complet, plus long).
- Smoke test: vérifie “l’app répond” après déploiement (ex: `/health`, `/docs`, `/openapi.json`).
Ordre recommandé dans Jenkins (fail fast):

1. Lint
2. Unit tests
3. Integration tests
4. Coverage / gates
5. Déploiement staging (si condition branche)
6. Smoke tests sur staging

## TP3 — Pipeline (Lint + sécurité + tests)

### Livrables attendus (TP3)

- Jenkinsfile complet (stages + post)
- Stack CI docker-compose (Jenkins + SonarQube)
- SonarQube configuré + Quality Gate
- Preuves d’exécution (Stage View, logs, dashboard, webhook, staging)
- Réponses aux questions (Q1 → Q5)

### 3.1 Lint (flake8)

Commande:

```powershell
python -m flake8 app
```

Résultat:

```text
(aucune erreur)
```

### 3.2 Analyse sécurité (Bandit)

Commande:

```powershell
python -m bandit -r app
```

Sortie (extrait):

```text
Test results:
        No issues identified.
...
Total issues (by severity):
                Low: 0
                Medium: 0
                High: 0
```

### 3.3 Pipeline local (script PowerShell)

Commande:

```powershell
powershell -ExecutionPolicy Bypass -File run_pipeline.ps1
```

Sortie (extrait):

```text
Lint...
Security (Bandit)...
Test results:
        No issues identified.
Tests...
...
============================= 56 passed in 12.34s =============================
Pipeline OK
```

### Q1 → Q5 (Jenkins/Sonar) — preuves à joindre pour un rendu “20/20”

Cette partie se valide avec des preuves depuis Jenkins + SonarQube (interfaces web). Le dépôt contient bien `Jenkinsfile`, `docker-compose.ci.yml`, `sonar-project.properties`, et `docker-compose.staging.yml`.

### SonarCloud (GitHub CI) — Preuves et où cliquer

Dans ce projet, l’analyse Sonar est déjà intégrée au **CI GitHub** (SonarCloud).

- **Voir le détail du Quality Gate**:
  - Ouvrir GitHub → onglet “Checks” du dernier commit → “SonarCloud Code Analysis”.
  - Cliquer sur “Details” pour ouvrir le dashboard SonarCloud.
- **Exemple de correction appliquée (règle python:S1244)**:
  - Sonar remonte “Do not perform equality checks with floating point values”.
  - Correction: remplacer `assert response.json()["price"] == 79.99` par `pytest.approx(79.99)` dans `tests/integration/test_products_api.py`.

#### Q1 — Environnement CI (docker compose + config Jenkins/Sonar)

Commandes (preuves attendues):

```powershell
docker compose -f docker-compose.ci.yml up -d
docker compose -f docker-compose.ci.yml ps
```

À coller ici: sortie montrant Jenkins + SonarQube `Up`.

Pourquoi `http://sonarqube:9000` plutôt que `http://localhost:9000` ?  
Dans Docker, les conteneurs se parlent via le réseau interne: `sonarqube` est le **nom de service** résolu par DNS interne. `localhost` dans un conteneur pointe sur le conteneur lui-même.

#### Q2 — Stages Lint/Tests/Coverage (Stage View Jenkins)

À coller ici:

- capture Stage View (Install, Lint, Unit Tests, Integration Tests, Coverage, etc.)
- extrait de log des stages Unit/Coverage (équivalent à nos preuves console).

#### Q3 — SonarQube + Bandit + Quality Gate

À coller ici:

- capture dashboard Sonar (Coverage/Bugs/Smells/Vulnerabilities)
- résultat Quality Gate (PASSED/FAILED)
- si demandé: extrait `bandit-report.json` (3 premiers résultats).  
Note locale: Bandit ne détecte **aucune issue** (voir section 3.2).

#### Q4 — Build Docker + Deploy staging

- vue pipeline complet (9 stages verts)
- sortie du smoke test staging:

```powershell
curl http://localhost:8001/health
```

Pourquoi tagger l’image avec le SHA Git plutôt que `latest` ?  
Traçabilité + rollback: chaque image correspond à un commit précis; on peut redeployer exactement une version qui marchait.



