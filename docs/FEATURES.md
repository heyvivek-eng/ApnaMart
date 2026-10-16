# Feature completion checklist

Status describes only what is present in this deliverable.

## Implemented MVP

- [x] Monorepo layout, Compose services, PostgreSQL persistence and Alembic initial migration
- [x] FastAPI versioned routes, OpenAPI docs and health route
- [x] Argon2 password hashing, registration, login, signed bearer token and current-user endpoint
- [x] Database-backed product catalog with name search, category filter, sorting and pagination parameters
- [x] Idempotent 1,000-item synthetic demo catalog with the documented category distribution and local placeholder image
- [x] Paginated storefront catalog, category filtering, price sorting, and load-more interaction
- [x] Authenticated customer cart; backend stock checks and authoritative price calculation
- [x] COD order placement, stock deduction, purchase-detail snapshots and unpaid status
- [x] Storefront search/category filters, product detail routes, account registration/sign-in, cart quantity controls and COD checkout
- [x] Persistent light/dark theme across storefront routes
- [x] Customer order listing and ownership-protected order detail
- [x] Responsive original storefront and demo catalog seeder
- [x] Backend tests for catalog search, cart/order calculation, COD unpaid state and order ownership

## Not implemented (do not use as a live commerce service)

- [ ] Multi-vendor seller application/approval, seller-owned listings, parent/seller suborders, inventory ledger and seller isolation
- [ ] Email verification, password reset, addresses, profile edit, sessions/logout, wishlists, coupon/tax/shipping quotes
- [ ] Razorpay order creation, signature/webhook verification, refunds, reconciliation and payment-event idempotency
- [ ] Cancellation, shipment tracking, returns, reviews, support, notifications and audit logs
- [ ] Admin/support authorization workflows, moderation, reports, commissions, seller ledger and payouts
- [ ] Upload service, S3-compatible storage, Redis, rate limiting, CSRF/session-cookie deployment, backups automation
- [ ] Frontend unit/e2e tests, Playwright flows, production hardening and deployment review

No endpoint reports a Razorpay payment or seller payout as successful. Only COD checkout is available, and it remains unpaid pending collection.
