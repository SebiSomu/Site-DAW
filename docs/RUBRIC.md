# Rubric progress

Status of every criterion in the grading rubric (`Barem_evaluare_proiect_web.pdf`, kept locally and not in git), with where to find the proof.

Legend: ✅ done · 🟡 partial · ⬜ not started

## Grade 2 — Core features and application architecture

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 2.01 | Database in 3NF | ✅ | [`docs/DATABASE.md`](DATABASE.md), ER diagram, `backend/tests/test_models.py` |
| 2.02 | ≥4 use cases | ✅ | Working end to end in the browser: UC1 browse catalogue (`/products`, `/products/<slug>`), UC2 cart (`/cart`, server-priced through `POST /api/cart/validate`), UC3 register, log in and log out (`/register`, `/login`, `/account`), UC5 order history, detail and cancel (`/account/orders`), UC6 reviews of bought jars (product page). UC4 checkout places the order but card payment arrives in phase 6. Remaining: UC7 contact, UC8 admin. Tests: `backend/tests/test_shop.py` |
| 2.03 | MVC / Repository | ✅ | Models (`backend/app/models/`), Views (Svelte pages in `src/pages/`), Controllers (`backend/app/controllers/`), plus Repository (`backend/app/repositories/`) and Service (`backend/app/services/`) layers. Example flow: `ProductsPage.svelte` → `GET /api/products` → `catalog_controller` → `CatalogService` → `ProductRepository` → `Product` |
| 2.04 | Images, text, tables, links | ✅ | Watercolour plates and jar illustrations, descriptions, tables ("About this jar", cart, order history, order detail), navigation, breadcrumb, footer and category links. Real product photos and legal pages are still to come |

## Grade 3 — Object-oriented programming and access control

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 3.01 | ≥3 classes | ✅ | 80+ backend classes plus `ApiClient`, `ApiError`, `Router`, `CartStore` and `AuthStore` on the frontend, see below |
| 3.02 | ≥1 interface | ✅ | `IRepository` (ABC with abstract methods) in `backend/app/repositories/base.py`, implemented through `SqlAlchemyRepository` by every repository. `PaymentGateway` (`backend/app/services/payments/gateway.py`), implemented by `StripeGateway` and `FakeGateway`. `FileValidator` comes in phase 7 |
| 3.03 | Authentication | ✅ | Pages `/login`, `/register`, log out on `/account` (`AuthStore` in `src/lib/stores/auth.svelte.ts`). API `/api/auth/register`, `/login`, `/logout`, `/me`, `/session` (`backend/app/controllers/auth_controller.py` → `AuthService`); Flask-Login session cookie (HttpOnly, SameSite=Lax, Secure in prod); scrypt hashes. Tests: `backend/tests/test_auth.py` |
| 3.04 | Authorization | ✅ | Roles `client`/`admin`; `@login_required` and `@role_required(RoleName.ADMIN)` (`backend/app/security/access.py`): guest → 401, client → 403, admin → 200 (`test_role_required_enforces_admin_role`). Ownership: a client cannot read or cancel another client's order or use their address, 404 (`test_client_only_sees_their_own_orders`, `test_address_of_another_client_cannot_be_archived_or_used`). Reviews only after a purchase (`test_review_needs_a_purchase`). Frontend guard: `AuthGate.svelte` (UX only) |

### 3.01 — Classes

| Group | Classes | File |
|---|---|---|
| Domain models | `User`, `Role`, `Address`, `Category`, `Product`, `ProductImage`, `Ingredient`, `Order`, `OrderItem`, `OrderStatus`, `Payment`, `Review`, `ContactMessage` | `backend/app/models/` |
| Mixins | `IdMixin`, `TimestampMixin` | `backend/app/models/mixins.py` |
| Enumerations | `RoleName`, `OrderStatusCode`, `PaymentStatus`, `PaymentProvider`, `ProductSort` | `backend/app/models/enums.py`, `backend/app/repositories/product_repository.py` |
| Repositories | `SqlAlchemyRepository`, `UserRepository`, `AddressRepository`, `RoleRepository`, `CategoryRepository`, `IngredientRepository`, `ProductRepository`, `OrderRepository`, `OrderStatusRepository`, `PaymentRepository`, `ReviewRepository`, `ContactMessageRepository` | `backend/app/repositories/` |
| Value objects | `ProductPage`, `CartLine`, `CartSummary`, `CheckoutSession`, `PaymentEvent`, `SeedReport`, `CategorySeed`, `ProductSeed` | `backend/app/repositories/product_repository.py`, `backend/app/models/cart.py`, `backend/app/seed/` |
| Services | `AuthService`, `CatalogService`, `CartService`, `AddressService`, `OrderService`, `ReviewService`, `StripeGateway`, `FakeGateway`, `ActivityLogger`, `DatabaseSeeder` | `backend/app/services/`, `backend/app/seed/seeder.py` |
| Errors | `AppError`, `ValidationError`, `AuthenticationError`, `ForbiddenError`, `NotFoundError`, `ConflictError`, `OutOfStockError`, `CheckoutAlreadyPaidError`, `PaymentError`, `WebhookError` | `backend/app/errors.py` |
| Request/response schemas | `RequestSchema`, `RegisterRequest`, `LoginRequest`, `UserResponse`, `ProductQuery`, `CategoryResponse`, `CategoryRef`, `ImageResponse`, `ReviewResponse`, `ProductSummary` → `ProductDetail`, `ProductPageResponse`, `CartRequest`, `CartResponse`, `AddressRequest`, `AddressResponse`, `OrderRequest`, `OrderSummary` → `OrderDetail`, `ReviewRequest` | `backend/app/schemas/` |
| Frontend | `ApiClient`, `ApiError` (extends `Error`), `Router`, `CartStore`, `AuthStore` | `src/lib/api/client.ts`, `src/lib/router/router.svelte.ts`, `src/lib/stores/` |
| Configuration | `BaseConfig`, `DevelopmentConfig`, `TestingConfig`, `ProductionConfig` | `backend/app/config.py` |

Classes with real behaviour, good to show the teacher:

- `User`: `set_password()`, `check_password()` (scrypt), `full_name`, `is_admin`
- `Order`: `total_cents` and `is_cancellable`, computed from its items and status
- `Product`: `is_in_stock`, `average_rating`
- `ProductRepository`: `search()` with filters, sorting and pagination
- `DatabaseSeeder`: `run()` builds the whole catalogue through the repositories

Counted with: `grep -rE "^class " backend/app | wc -l`

## Grade 4 — OOP concepts and interactive elements

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 4.01 | Inheritance | ✅ | Repositories inherit `SqlAlchemyRepository`; configs inherit `BaseConfig`; models inherit mixins; `AppError` → `ValidationError`, `AuthenticationError`, `ForbiddenError`, `NotFoundError`, `ConflictError` → `OutOfStockError` (`backend/app/errors.py`); `OrderDetail` extends `OrderSummary` (`backend/app/schemas/shop.py`); `StripeGateway` and `FakeGateway` extend `PaymentGateway`; `ProductDetail` extends `ProductSummary` (`backend/app/schemas/catalog.py`); `ApiError` extends `Error` (`src/lib/api/client.ts`) |
| 4.02 | ≥2 exception types handled | ✅ | `backend/app/errors.py` maps the `AppError` family (including `PaymentError` and `WebhookError`; `StripeGateway` catches every `stripe.StripeError` and raises `PaymentError`), Pydantic `ValidationError`, SQLAlchemy `IntegrityError`, Flask-WTF `CSRFError`, Werkzeug `HTTPException` and unexpected errors (500) to JSON `{"error": ...}`. Tests: duplicate email → 409, invalid input → 400, guest → 401, unknown route → 404 |
| 4.03 | Image carousel | ✅ | `src/lib/components/Carousel.svelte` on the home page: four fruit watercolours as recipe-book pages that turn over (3D page turn), autoplay every 7 s with a pause button, previous/next buttons, page dots, arrow keys, swipe on touch screens, pauses on hover and focus, `aria-roledescription="carousel"` and `aria-live` when paused |
| 4.04 | Animation | ✅ | `src/styles/animations.css`: `@keyframes sway` (jar cards and pinned pictures sway like paper in a draught, each with its own tilt, duration and delay), tape that lifts on hover, `@keyframes rise` scroll-linked entrances (`animation-timeline: view()`); Svelte page-turn transition in the carousel. All switched off under `prefers-reduced-motion` (autoplay off too) |

## Grade 5 — Styling and responsive design

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 5.01 | ≥2 CSS files, ≥10 properties | ✅ | 5 files in `src/styles/` (`variables.css`, `base.css`, `layout.css`, `components.css`, `animations.css`) plus scoped component styles; 80+ distinct properties, e.g. custom properties, `grid-template-columns`, `clip-path`, `perspective`, `aspect-ratio`, `object-fit`, `transform-origin`, `animation-timeline`, `clamp()` sizes. Fonts self-hosted through `@fontsource-variable` |
| 5.02 | Responsive | ✅ | Mobile-first, breakpoints 600px and 1024px: menu button below 1024px, jar grid 2 → 4 columns, hero and product page 1 → 2 columns, carousel page stacks on phones, tables scroll sideways. Screenshots: [`docs/screenshots/`](screenshots/) (phone 390px, tablet 768px, desktop 1440px) |

## Grade 6 — Testing and development automation

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 6.01 | ≥5 unit tests | ✅ | 139 pytest tests in `backend/tests/` and 30 Vitest tests in `src/` (`npm test`) |
| 6.02 | Git | ✅ | GitHub repo `SebiSomu/Site-DAW` |
| 6.03 | GitHub Actions CI | 🟡 | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml): backend tests + frontend check, tests and build. Done once a run on GitHub is confirmed green (screenshot of the Actions tab) |

## Grade 7 — Monitoring and publishing

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 7.01 | Activity log file | 🟡 | `ActivityLogger` (`backend/app/services/activity_logger.py`) → `backend/logs/activity.log`, `timestamp \| level \| ip \| user_id \| action \| details`, rotating 1 MB × 5. Logs register, login, login_failed, logout, access_denied, csrf_rejected, cart_validated, address_added, address_archived, order_created, order_cancelled, review_posted. Pending: payment and admin actions and the admin log viewer (phase 7) |
| 7.02 | Hosting | ⬜ | |

## Grade 8 — Optimisation and external services

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 8.01 | Lighthouse SEO ≥90 | 🟡 | `Seo.svelte` on every page (unique title, meta description, canonical, Open Graph, `noindex` on 404s); `lang="en"`, viewport meta; crawlable `<a href>` links; `alt` on every image; `/robots.txt` and `/sitemap.xml` generated by Flask (`backend/app/controllers/seo_controller.py`, tests in `backend/tests/test_catalog.py`). Pending: Lighthouse report on the deployed site |
| 8.02 | Online payments (Stripe) | ⬜ | |

## Grade 9 — Security, level I

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 9.01 | CSRF | ✅ | Flask-WTF `CSRFProtect` on every non-GET route; token from `GET /api/csrf` sent as `X-CSRFToken`; SameSite=Lax cookie. Test: `test_post_without_csrf_token_is_rejected` (400 + logged) |
| 9.02 | XSS | 🟡 | Svelte escapes all output and there is no `{@html}`. Review comments and order notes are stored as plain text through `nh3` (`backend/app/security/sanitize.py`). Tests: `test_review_is_posted_once_and_stored_as_plain_text`, `test_order_notes_are_stored_as_plain_text`. Pending: Content-Security-Policy (phase 8) |
| 9.03 | SQL Injection | ✅ | ORM-only queries with bound parameters, LIKE wildcards escaped (`ProductRepository._escape_like`), query string validated by Pydantic (`ProductQuery`). Tests: `test_search_is_safe_against_sql_injection` (repository) and `test_products_search_is_safe_against_sql_injection` (`GET /api/products?q=' OR 1=1 --` → 200, 0 results) |
| 9.04 | Max 12 MB upload | ⬜ | |
| 9.05 | Allowed extensions | ⬜ | |

## Grade 10 — Security, level II

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 10.01 | Rate limiting | ⬜ | |
| 10.02 | CAPTCHA | ⬜ | |
| 10.03 | Steganography protection | ⬜ | |
| 10.04 | Security headers grade A | ⬜ | |
| 10.05 | `.htaccess` | ⬜ | |
