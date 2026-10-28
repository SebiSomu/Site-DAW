# Barem progress

Status of every criterion in [`Barem_evaluare_proiect_web.md`](../Barem_evaluare_proiect_web.md), with where to find the proof.

Legend: ✅ done · 🟡 partial · ⬜ not started

## Nota 2 — Funcționalități de bază și arhitectura aplicației

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 2.01 | Database in 3NF | ✅ | [`docs/DATABASE.md`](DATABASE.md), ER diagram, `backend/tests/test_models.py` |
| 2.02 | ≥4 use cases | ⬜ | |
| 2.03 | MVC / Repository | 🟡 | Models + Repository layer (`backend/app/models/`, `backend/app/repositories/`), Service layer (`backend/app/services/`), Controllers (`backend/app/controllers/`); Svelte views pending |
| 2.04 | Images, text, tables, links | ⬜ | |

## Nota 3 — Programare orientată pe obiecte și controlul accesului

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 3.01 | ≥3 classes | ✅ | 55 backend classes, see below |
| 3.02 | ≥1 interface | ✅ | `IRepository` (ABC with abstract methods) in `backend/app/repositories/base.py`, implemented through `SqlAlchemyRepository` by every repository. `PaymentGateway` and `FileValidator` come in phases 6–7 |
| 3.03 | Authentication | ✅ | `/api/auth/register`, `/login`, `/logout`, `/me` (`backend/app/controllers/auth_controller.py` → `AuthService`); Flask-Login session cookie (HttpOnly, SameSite=Lax, Secure in prod); scrypt hashes. Tests: `backend/tests/test_auth.py` |
| 3.04 | Authorization | 🟡 | Roles `client`/`admin`; `@login_required` and `@role_required(RoleName.ADMIN)` (`backend/app/security/access.py`): guest → 401, client → 403, admin → 200 (`test_role_required_enforces_admin_role`). Pending: ownership checks on orders (phase 5), frontend route guards (UX only) |

### 3.01 — Classes

| Group | Classes | File |
|---|---|---|
| Domain models | `User`, `Role`, `Address`, `Category`, `Product`, `ProductImage`, `Ingredient`, `Order`, `OrderItem`, `OrderStatus`, `Payment`, `Review`, `ContactMessage` | `backend/app/models/` |
| Mixins | `IdMixin`, `TimestampMixin` | `backend/app/models/mixins.py` |
| Enumerations | `RoleName`, `OrderStatusCode`, `PaymentStatus`, `PaymentProvider`, `ProductSort` | `backend/app/models/enums.py`, `backend/app/repositories/product_repository.py` |
| Repositories | `SqlAlchemyRepository`, `UserRepository`, `AddressRepository`, `RoleRepository`, `CategoryRepository`, `IngredientRepository`, `ProductRepository`, `OrderRepository`, `OrderStatusRepository`, `PaymentRepository`, `ReviewRepository`, `ContactMessageRepository` | `backend/app/repositories/` |
| Value objects | `ProductPage`, `SeedReport`, `CategorySeed`, `ProductSeed` | `backend/app/repositories/product_repository.py`, `backend/app/seed/` |
| Services | `AuthService`, `ActivityLogger`, `DatabaseSeeder` | `backend/app/services/`, `backend/app/seed/seeder.py` |
| Errors | `AppError`, `ValidationError`, `AuthenticationError`, `ForbiddenError`, `NotFoundError`, `ConflictError` | `backend/app/errors.py` |
| Request/response schemas | `RequestSchema`, `RegisterRequest`, `LoginRequest`, `UserResponse` | `backend/app/schemas/auth.py` |
| Configuration | `BaseConfig`, `DevelopmentConfig`, `TestingConfig`, `ProductionConfig` | `backend/app/config.py` |

Classes with real behaviour, good to show the teacher:

- `User`: `set_password()`, `check_password()` (scrypt), `full_name`, `is_admin`
- `Order`: `total_bani` and `is_cancellable`, computed from its items and status
- `Product`: `is_in_stock`, `average_rating`
- `ProductRepository`: `search()` with filters, sorting and pagination
- `DatabaseSeeder`: `run()` builds the whole catalogue through the repositories

Counted with: `grep -rE "^class " backend/app | wc -l`

## Nota 4 — Concepte OOP și elemente interactive

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 4.01 | Inheritance | ✅ | Repositories inherit `SqlAlchemyRepository`; configs inherit `BaseConfig`; models inherit mixins; `AppError` → `ValidationError`, `AuthenticationError`, `ForbiddenError`, `NotFoundError`, `ConflictError` (`backend/app/errors.py`) |
| 4.02 | ≥2 exception types handled | ✅ | `backend/app/errors.py` maps the `AppError` family, Pydantic `ValidationError`, SQLAlchemy `IntegrityError`, Flask-WTF `CSRFError`, Werkzeug `HTTPException` and unexpected errors (500) to JSON `{"error": ...}`. Tests: duplicate email → 409, invalid input → 400, guest → 401, unknown route → 404 |
| 4.03 | Image carousel | ⬜ | |
| 4.04 | Animation | ⬜ | |

## Nota 5 — Stilizare și design responsive

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 5.01 | ≥2 CSS files, ≥10 properties | ⬜ | |
| 5.02 | Responsive | ⬜ | |

## Nota 6 — Testare și automatizarea dezvoltării

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 6.01 | ≥5 unit tests | ✅ | 43 pytest tests in `backend/tests/` |
| 6.02 | Git | ✅ | GitHub repo `SebiSomu/Site-DAW` |
| 6.03 | GitHub Actions CI | 🟡 | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml): backend tests + frontend check/build. Done once the first run on GitHub is green (screenshot of the Actions tab) |

## Nota 7 — Monitorizare și publicarea aplicației

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 7.01 | Activity log file | 🟡 | `ActivityLogger` (`backend/app/services/activity_logger.py`) → `backend/logs/activity.log`, `timestamp \| level \| ip \| user_id \| action \| details`, rotating 1 MB × 5. Logs register, login, login_failed, logout, access_denied, csrf_rejected. Pending: order/review/admin actions and the admin log viewer (phase 7) |
| 7.02 | Hosting | ⬜ | |

## Nota 8 — Optimizare și integrarea serviciilor externe

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 8.01 | Lighthouse SEO ≥90 | ⬜ | |
| 8.02 | Online payments (Stripe) | ⬜ | |

## Nota 9 — Securitate, nivelul I

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 9.01 | CSRF | ✅ | Flask-WTF `CSRFProtect` on every non-GET route; token from `GET /api/csrf` sent as `X-CSRFToken`; SameSite=Lax cookie. Test: `test_post_without_csrf_token_is_rejected` (400 + logged) |
| 9.02 | XSS | ⬜ | |
| 9.03 | SQL Injection | 🟡 | ORM-only queries; `test_search_is_safe_against_sql_injection`. Needs the API layer |
| 9.04 | Max 12 MB upload | ⬜ | |
| 9.05 | Allowed extensions | ⬜ | |

## Nota 10 — Securitate, nivelul II

| # | Criterion | Status | Proof |
|---|---|:-:|---|
| 10.01 | Rate limiting | ⬜ | |
| 10.02 | CAPTCHA | ⬜ | |
| 10.03 | Steganography protection | ⬜ | |
| 10.04 | Security headers grade A | ⬜ | |
| 10.05 | `.htaccess` | ⬜ | |
