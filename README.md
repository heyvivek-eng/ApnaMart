# ApnaMart

An original Indian marketplace MVP: a Next.js storefront backed by FastAPI and PostgreSQL. This is a runnable foundation, not a claim of a production-ready or complete multi-vendor commerce platform. The feature checklist in `docs/FEATURES.md` calls out important work still needed.

## Requirements

- Docker Desktop with Docker Compose
- For local development without Docker: Python 3.12+ and Node.js 22+

## Start with Docker

1. Copy `.env.example` to `.env`. Change `JWT_SECRET` and the local database password before exposing the service to any network.
2. Start the stack: `docker compose up --build`
3. In another terminal, seed clearly labelled sample catalog entries:
   `docker compose exec api python -m scripts.seed_demo`
4. Open the storefront at <http://localhost:3000>, API docs at <http://localhost:8000/docs>, and health check at <http://localhost:8000/health>.

The API container applies Alembic migrations at startup. Database data persists in the `postgres_data` volume.

The demo seeder idempotently adds 1,000 synthetic catalog products (200 Electronics & Accessories, 250 Fashion & Footwear, 200 Home & Kitchen, 100 Beauty & Personal Care, 100 Books & Stationery, and 150 Sports, Toys & Lifestyle). It preserves existing products, users, prices, stock, and SKUs, while assigning or refreshing product images for generated listings and filling missing images on existing products. Product photographs are bundled under `frontend/public/images/products/` and selected by product name and category; the placeholder image is only a fallback when a photo cannot load. Photos are sourced from Unsplash and used under the [Unsplash License](https://unsplash.com/license). Demo prices and stock values are sample data, not real offers or inventory claims. Re-running the seeder skips duplicate generated SKUs and safely updates their image paths.

On Windows PowerShell, run the seeder from the project root after the stack is running:

```powershell
docker compose exec api python -m scripts.seed_demo
```

The storefront requests 24 products at a time and uses the API's `offset`, `sort`, `q`, and `category` parameters for load-more, sorting, search, and category filtering.

## Local development

Backend (from `backend/`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///./berozgaarbazar.db"
$env:JWT_SECRET = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(48))
alembic upgrade head
python scripts/seed_demo.py
uvicorn app.main:app --reload
```

Frontend (from `frontend/`):

```powershell
npm install
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000/api/v1"
npm run dev
```

The `.env.example` values are placeholders for local development only; replace the database password and JWT secret before starting Compose. There is no built-in JWT signing secret: the API refuses to start if the configured secret is shorter than 32 characters. `NEXT_PUBLIC_API_URL` is a public API address, not a secret. Never put payment secrets or signing keys in `NEXT_PUBLIC_*`.

## Tests and checks

From `backend/`, run `pytest`. From `frontend/`, run `npm run typecheck` and `npm run build`. Tests use an isolated in-memory SQLite database. Docker startup is the documented PostgreSQL migration smoke test.

## API overview

- `POST /api/v1/auth/register` and form-encoded `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/products?q=&category=&sort=&limit=&offset=` (maximum page size: 100)
- `GET /api/v1/products/{id}`
- Authenticated cart: `GET /api/v1/cart`, `POST /api/v1/cart/items`, `PUT/DELETE /api/v1/cart/items/{product_id}`
- Authenticated order placement (COD only): `POST /api/v1/orders/checkout`
- Customer-scoped order access: `GET /api/v1/orders` and `GET /api/v1/orders/{id}`

Money is represented as integer paise throughout. Checkout computes the total from database product prices, snapshots essential product details in order items, decrements available stock, and keeps COD unpaid until collection. Demo catalog data is synthetic and is not a real offer.

## Security and operations

- Passwords use the recommended Argon2 password hashing configuration.
- API access uses short-lived signed bearer tokens. The MVP storefront stores the access token in browser local storage for demonstration; this is not the preferred production session design. Use secure HttpOnly cookies, CSRF protection and a deliberate refresh/revocation strategy before production.
- CORS is allowlisted to `FRONTEND_ORIGIN`; configure exact deployment origins.
- Database access uses SQLAlchemy parameterized statements. Secrets are configured using environment variables.
- Take regular PostgreSQL backups, store them outside the database host, and test restoration. Example: `docker compose exec -T db pg_dump -U bbazar berozgaarbazar > backup.sql`; restore only into a separately verified target with `psql`.
- No Razorpay credentials, live payment integration, email provider, storage credentials, or real seller payout transfers are included.

## Troubleshooting

- **Catalog unavailable:** ensure Docker services are running and `api` is healthy; open `/health`.
- **No products:** run `docker compose exec api python scripts/seed_demo.py`.
- **Database migration fails:** check `DATABASE_URL` and PostgreSQL health; inspect `docker compose logs api db`.
- **Browser CORS error:** `FRONTEND_ORIGIN` must exactly match the storefront origin. Recreate the API container after changing `.env`.
- **Port already in use:** change the host-side port mappings in `docker-compose.yml`.
- **Docker build issue:** check Docker Desktop is running, then run `docker compose build --no-cache`.
