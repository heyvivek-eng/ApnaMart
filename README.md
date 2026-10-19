# ApnaMart 🛍️

### An Original Indian E-Commerce Marketplace MVP

ApnaMart is an Indian e-commerce marketplace MVP built with **Next.js, TypeScript, FastAPI, and PostgreSQL**. It provides a foundation for exploring modern storefront development, REST APIs, product catalog management, authentication, shopping carts, and order placement.

> **Project status:** This is a runnable MVP foundation, not a production-ready or fully featured multi-vendor commerce platform. See [`docs/FEATURES.md`](docs/FEATURES.md) for the feature checklist and remaining work.

---

## 📸 Website Screenshots

Explore the ApnaMart storefront through the screenshots below.

### 🏠 Homepage

![ApnaMart Homepage](docs/screenshots/Screenshot%202026-10-17%20014705.png)

### 🛍️ Shopping Experience

![ApnaMart Shopping Experience](docs/screenshots/Screenshot%202026-10-17%20014806.png)

### 💻 Storefront Preview

![ApnaMart Storefront Preview](docs/screenshots/Screenshot%202026-10-17%20014850.png)

---

## ✨ Key Features

- Responsive Next.js storefront
- Product catalog with search and category filtering
- Product sorting and pagination through load-more functionality
- User registration, login, and authenticated API access
- Shopping cart management
- Customer-scoped order history and order details
- Cash on Delivery (COD) checkout
- PostgreSQL database with SQLAlchemy
- Database migrations using Alembic
- Docker Compose development environment
- Synthetic demo catalog with product image assets
- API documentation through FastAPI Swagger UI
- Health endpoint for service checks

*The features listed describe the current MVP scope, not a claim that every marketplace or production feature is complete.*

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Infrastructure | Docker Compose |
| API Documentation | FastAPI Swagger UI |
| Product Images | Local image assets sourced from Unsplash |

---

## 📋 Requirements

- Docker Desktop with Docker Compose
- Python 3.12+ for local backend development without Docker
- Node.js 22+ for local frontend development without Docker
- Git for cloning and version control

---

## 🚀 Getting Started with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/heyvivek-eng/ApnaMart.git
cd ApnaMart
```

### 2. Configure Environment Variables

Copy the example environment file.

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Git Bash:**

```bash
cp .env.example .env
```

Review `.env` and configure the required values. Replace placeholder secrets and the local database password before exposing services to any network.

### 3. Start the Application

```bash
docker compose up --build
```

Wait for the services to start.

### 4. Seed the Demo Catalog

Open another terminal in the project root and run:

```bash
docker compose exec api python -m scripts.seed_demo
```

The seeder adds synthetic sample products and can be run again without duplicating generated SKUs.

### 5. Open ApnaMart

| Service | URL |
|---|---|
| Storefront | http://localhost:3000 |
| API Documentation | http://localhost:8000/docs |
| API Health Check | http://localhost:8000/health |

The API container applies Alembic migrations at startup. PostgreSQL data persists in the `postgres_data` Docker volume.

---

## 🛒 Demo Product Catalog

The demo seeder creates **1,000 synthetic catalog products** across six categories.

| Category | Products |
|---|---:|
| Electronics & Accessories | 200 |
| Fashion & Footwear | 250 |
| Home & Kitchen | 200 |
| Beauty & Personal Care | 100 |
| Books & Stationery | 100 |
| Sports, Toys & Lifestyle | 150 |
| **Total** | **1,000** |

Product photographs are bundled under `frontend/public/images/products/` and selected by product name and category. A placeholder image is used only as a fallback when a photograph cannot load.

Photographs are sourced from [Unsplash](https://unsplash.com/) and used under the [Unsplash License](https://unsplash.com/license).

> Demo prices and stock values are sample data, not real offers or inventory claims.

The seeder preserves existing products, users, prices, stock, and SKUs while updating image paths as documented in the project implementation.

---

## 💻 Local Development

You can also run the backend and frontend separately without Docker.

### Backend Setup

Run these commands from the `backend/` directory in Windows PowerShell.

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

The commands above configure SQLite for local development. PostgreSQL is used by the documented Docker setup.

### Frontend Setup

Open another terminal and navigate to `frontend/`.

```powershell
npm install
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000/api/v1"
npm run dev
```

Open http://localhost:3000 in your browser.

> `NEXT_PUBLIC_API_URL` is a public API address, not a secret. Never place payment credentials, signing keys, or other secrets in `NEXT_PUBLIC_*` variables.

The `.env.example` values are placeholders for local development. Configure a secure JWT secret of at least 32 characters and a suitable database password before exposing the application to a network.

---

## 🔌 API Overview

The FastAPI backend exposes REST endpoints for authentication, products, carts, and orders.

### Authentication

- `POST /api/v1/auth/register` — Register a user
- `POST /api/v1/auth/login` — Authenticate using form-encoded credentials
- `GET /api/v1/auth/me` — Get the authenticated user's information

### Products

- `GET /api/v1/products` — List products with search, filtering, sorting, and pagination
- `GET /api/v1/products/{id}` — Get a product by ID

Supported query parameters include `q`, `category`, `sort`, `limit`, and `offset`. The maximum page size is 100 products.

### Shopping Cart

- `GET /api/v1/cart` — Retrieve the authenticated user's cart
- `POST /api/v1/cart/items` — Add a product to the cart
- `PUT /api/v1/cart/items/{product_id}` — Update a cart item
- `DELETE /api/v1/cart/items/{product_id}` — Remove a cart item

### Orders

- `POST /api/v1/orders/checkout` — Place an order using the supported COD checkout flow
- `GET /api/v1/orders` — List the authenticated customer's orders
- `GET /api/v1/orders/{id}` — Retrieve an order belonging to the authenticated customer

For interactive API testing, visit [FastAPI Swagger UI](http://localhost:8000/docs) after starting the application.

---

## 🔐 Security and Operations

- Passwords are hashed using Argon2.
- API access uses short-lived signed bearer tokens.
- The current MVP storefront stores its access token in browser local storage for demonstration; this is not the preferred production session design.
- Production deployment should use secure HttpOnly cookies, CSRF protection, and a deliberate token refresh and revocation strategy.
- CORS is allowlisted through `FRONTEND_ORIGIN`; configure exact deployment origins.
- SQLAlchemy is used for database access with parameterized statements.
- Secrets are supplied through environment variables.
- Monetary values are represented as integer paise.
- Checkout calculates totals from database prices, snapshots essential product details in order items, decrements available stock, and keeps COD orders unpaid until collection.

**Not included:** Live Razorpay integration, a production email provider, external storage credentials, and real seller payout transfers.

### Database Backups

Back up PostgreSQL regularly and test restoration against a separate, verified target.

Example backup command:

```bash
docker compose exec -T db pg_dump -U bbazar berozgaarbazar > backup.sql
```

Verify the database and user names in your configuration before running the command. Protect backup files because they may contain sensitive data.

---

## 🧪 Tests and Quality Checks

### Backend

Run from `backend/`:

```bash
pytest
```

### Frontend

Run from `frontend/`:

```bash
npm run typecheck
npm run build
```

Tests use an isolated in-memory SQLite database. Docker startup provides the documented PostgreSQL migration smoke test.

---

## 🗂️ Project Structure

```text
ApnaMart/
├── backend/       # FastAPI application and database logic
├── frontend/      # Next.js storefront
├── docs/          # Project documentation and screenshots
├── infra/         # Infrastructure resources, if present
├── scripts/       # Project scripts, if present
├── .env.example   # Example environment configuration
├── .gitignore
├── docker-compose.yml
└── README.md
```

The exact contents of optional directories may vary with the current project version.

---

## 🛠️ Troubleshooting

**Catalog unavailable**
- Confirm that Docker services are running.
- Check the API health endpoint at http://localhost:8000/health.

**No products visible**
- Run `docker compose exec api python -m scripts.seed_demo`.

**Database migration failure**
- Check `DATABASE_URL` and PostgreSQL health.
- Inspect logs with `docker compose logs api db`.

**Browser CORS error**
- Ensure `FRONTEND_ORIGIN` exactly matches the storefront origin.
- Recreate the API container after changing `.env`.

**Port already in use**
- Change the host-side port mappings in `docker-compose.yml`.

**Docker build issue**
- Ensure Docker Desktop is running.
- Try `docker compose build --no-cache`.

For further feature details and planned improvements, see [`docs/FEATURES.md`](docs/FEATURES.md).

---

## 👨‍💻 Developer

**Vivek Singh Chauhan**

GitHub: [@heyvivek-eng](https://github.com/heyvivek-eng)

Project Repository: [ApnaMart](https://github.com/heyvivek-eng/ApnaMart)

---

## 📄 License

No license is specified here. Check the repository for a `LICENSE` file before reusing or distributing this project.

---

*Built as a learning and development project focused on modern full-stack e-commerce architecture.*