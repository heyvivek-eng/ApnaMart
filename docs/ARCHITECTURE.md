# Architecture

The `frontend/` Next.js App Router application serves the storefront. It uses the public API base URL from `NEXT_PUBLIC_API_URL`; no secret values belong in frontend configuration.

`backend/` is a FastAPI service with versioned REST endpoints, Pydantic request/response models, SQLAlchemy 2.x entities and Alembic migrations. PostgreSQL is the container database; SQLite is supported for simple local development and tests. Roles exist in the data model, but authorization-sensitive administrative and seller workflows are intentionally not exposed in this MVP.

Order item name, SKU and unit-price snapshots preserve essential purchase information. Prices use integer paise. Product stock changes during checkout are database transactions, but robust concurrent stock reservation/expiry and idempotent order creation still need implementation before accepting real orders.

See `FEATURES.md` for the exact implementation boundary and outstanding requirements.
