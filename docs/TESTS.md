# Tests

Rubric 6.01. 485 backend tests (pytest, 58 of them check this document) and 184 frontend tests (Vitest), run on every push by GitHub Actions together with an Apache check of the deployed layout.

| Suite | Command | Coverage | Minimum enforced |
|---|---|---|---|
| Backend (`backend/tests/`) | `pytest` | 99.7% of lines and branches in `backend/app/` | 98% (`backend/.coveragerc`) |
| Frontend (`src/**/*.test.ts`) | `npm test` | 97% of lines, 94% of branches in `src/**/*.ts` | 90% lines, 85% branches (`vite.config.ts`) |
| Apache (`deploy/check-apache.sh`) | CI job "Apache, .htaccess and headers" | 46 HTTP checks against Apache 2.4 + mod_wsgi + mod_php | all must pass |

Coverage reports: `pytest --cov --cov-report=html` (then open `backend/htmlcov/index.html`) and `npm run coverage` (then open `coverage/index.html`). CI prints both totals in the run summary and keeps the HTML reports as the `backend-coverage` and `frontend-coverage` artifacts.

Frontend coverage is measured on the TypeScript modules, where the logic lives (API client, stores, router, payment, CAPTCHA, admin helpers). Svelte pages and components are checked in the browser runs recorded in `PLAN.md` (6.5, 7.6, 8.3).

## Test plan §8, item by item

Every name below is checked by `backend/tests/test_test_plan.py`, so this table cannot point at a test that was renamed or removed.

| # | Requirement | Tests |
|---|---|---|
| 1 | Password is hashed and verifies correctly | `test_models.py::test_password_is_hashed_with_scrypt_and_verifies`, `test_auth.py::test_register_creates_logged_in_client_with_hashed_password` |
| 2 | Login with wrong password → 401, logged as failed | `test_auth.py::test_login_with_wrong_password_is_rejected_and_logged` |
| 3 | Client on `/api/admin/*` → 403; guest → 401 | `test_auth.py::test_role_required_enforces_admin_role`, `test_admin_products.py::test_client_is_refused`, `test_admin_products.py::test_guest_is_asked_to_log_in`, `test_admin_orders.py::test_client_is_refused` |
| 4 | Client cannot read another user's order | `test_shop.py::test_client_only_sees_their_own_orders`, `test_checkout.py::test_another_clients_order_cannot_be_paid`, `test_shop.py::test_address_of_another_client_cannot_be_archived_or_used` |
| 5 | Cart total from server prices, client prices ignored | `test_shop.py::test_cart_total_uses_server_prices_and_merges_repeated_jars`, `test_shop.py::test_cart_rejects_a_client_supplied_price`, `test_shop.py::test_order_is_placed_at_server_price_and_awaits_payment` |
| 6 | Order rejected when quantity > stock | `test_shop.py::test_order_over_stock_is_rejected`, `test_checkout.py::test_pay_rechecks_stock`, `test_checkout.py::test_oversold_jar_is_refunded_and_the_order_cancelled` |
| 7 | Cancel allowed only before shipping | `test_shop.py::test_cancel_is_allowed_before_shipping`, `test_shop.py::test_cancel_is_refused_once_shipped_or_already_cancelled`, `test_checkout.py::test_a_shipped_paid_order_cannot_be_cancelled_or_refunded` |
| 8 | Review only for bought jars, one per jar | `test_shop.py::test_review_needs_a_purchase`, `test_shop.py::test_unpaid_order_does_not_count_as_a_purchase`, `test_checkout.py::test_paid_order_makes_its_jars_reviewable`, `test_models.py::test_one_review_per_user_and_product` |
| 9 | Valid webhook → order `Paid`, stock decreased | `test_checkout.py::test_paid_webhook_marks_the_order_paid_and_takes_the_stock`, `test_checkout.py::test_resent_event_takes_the_stock_only_once` |
| 10 | Webhook with bad signature → 400 | `test_checkout.py::test_webhook_with_a_bad_signature_is_rejected_and_logged`, `test_payments.py::test_stripe_webhook_rejects_a_bad_signature`, `test_payments.py::test_stripe_webhook_rejects_a_tampered_payload` |
| 11 | POST without CSRF token → 400 | `test_auth.py::test_post_without_csrf_token_is_rejected`, `test_checkout.py::test_pay_requires_the_csrf_token`, `test_contact_and_logs.py::test_contact_form_needs_the_csrf_token`, `test_uploads.py::test_upload_without_a_csrf_token_is_refused` |
| 12 | Upload > 12 MB → 413 | `test_uploads.py::test_request_over_12_mb_is_refused_before_it_is_read`, `test_uploads.py::test_file_over_12_mb_is_rejected_with_413`, `test_admin_products.py::test_upload_over_12_mb_is_refused_with_413`, `test_htaccess.py::test_apache_body_limit_matches_flask` |
| 13 | Disallowed extension → 400 | `test_uploads.py::test_disallowed_extension_is_rejected`, `test_htaccess.py::test_uploads_serve_only_names_the_app_creates` |
| 14 | Fake image (renamed file) → 400 | `test_uploads.py::test_file_that_is_not_a_real_photo_is_rejected`, `test_uploads.py::test_photo_whose_name_lies_about_its_type_is_rejected`, `test_uploads.py::test_photo_over_40_megapixels_is_refused_before_it_is_decoded` |
| 15 | Appended data rejected; clean upload stored without EXIF | `test_uploads.py::test_photo_with_data_hidden_after_the_picture_is_rejected`, `test_uploads.py::test_clean_photo_is_re_encoded_to_webp_without_metadata`, `test_uploads.py::test_re_encoding_changes_the_pixels_that_could_carry_a_hidden_message`, `test_image_markers.py::test_png_end_ignores_bytes_after_iend` |
| 16 | Search with SQL injection string → safe | `test_catalog.py::test_products_search_is_safe_against_sql_injection`, `test_repositories.py::test_search_is_safe_against_sql_injection` |
| 17 | Review with `<script>` is sanitized | `test_shop.py::test_review_is_posted_once_and_stored_as_plain_text`, `test_contact_and_logs.py::test_message_text_is_stored_as_plain_text`, `test_admin_products.py::test_jar_text_is_stored_as_plain_text`, `test_security_headers.py::test_no_raw_html_rendering_in_the_frontend` |
| 18 | 101st request in a minute → 429 | `test_rate_limits.py::test_101st_request_in_a_minute_is_429_with_retry_after`, `test_rate_limits.py::test_sixth_attempt_on_a_strict_route_is_429` |
| 19 | Activity log line written on login | `test_auth.py::test_login_starts_session_and_is_logged`, `test_auth.py::test_login_with_wrong_password_is_rejected_and_logged` |

Frontend items from §8:

| Requirement | Tests |
|---|---|
| CartStore add, update, remove, total, persistence | `src/lib/stores/cart.test.ts` |
| ApiClient error mapping | `src/lib/api/client.test.ts` |
| Price formatting (`24.50 lei`) | `src/lib/format.test.ts` |

## Beyond §8

| Area | Backend | Frontend |
|---|---|---|
| Payments (Stripe gateway, webhook, refunds, races) | `test_payments.py`, `test_checkout.py` | `payment.test.ts`, `payment-redirect.test.ts` (only Stripe Checkout or this site is followed) |
| Admin (jars, photos, orders, messages, log viewer) | `test_admin_products.py`, `test_admin_orders.py`, `test_contact_and_logs.py` | `admin.test.ts` |
| Upload pipeline and image structure | `test_uploads.py`, `test_image_markers.py` | |
| CAPTCHA | `test_captcha.py` | `captcha.test.ts`, `stores/auth.test.ts` |
| Rate limiting | `test_rate_limits.py` | `api/client.test.ts` |
| Security headers, CSP, `.htaccess` | `test_security_headers.py`, `test_htaccess.py` | |
| Errors, health, CLI | `test_app_errors.py`, `test_health.py` | |
| Database (3NF constraints, repositories, seed) | `test_models.py`, `test_repositories.py`, `test_seed.py` | |
| Routing and navigation | | `router/router.test.ts`, `navigation.test.ts` |
| Content (jars, shelves, seasons, stars) | `test_catalog.py` | `jars.test.ts`, `shelves.test.ts`, `harvest.test.ts`, `format.test.ts` |

## How the tests are kept fast and isolated

Each backend test gets its own in-memory SQLite database. Seeding the shop (20 jars, two accounts hashed with full-strength scrypt) is done once per run into a template, then copied into each test's database with SQLite's backup API, which took the suite from about two minutes to under one without weakening password hashing. Payments use `FakeGateway` and the CAPTCHA uses `FakeVerifier`, so no test touches the network; rate limits are off except in `test_rate_limits.py`. Frontend tests that depend on dates pass in every time zone from UTC−11 to UTC+14.
