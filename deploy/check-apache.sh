#!/usr/bin/env bash
set -uo pipefail

BASE="${1:-http://localhost}"
UPLOAD_NAME="${2:-}"
FAILURES=0

status_of() {
  curl -s -o /dev/null -w "%{http_code}" "${@:2}" "$BASE$1"
}

header_of() {
  curl -s -D - -o /dev/null "$BASE$1" | tr -d '\r' | awk -v name="$2" 'BEGIN { IGNORECASE = 1 } index(tolower($0), tolower(name) ": ") == 1 { sub(/^[^:]+: /, ""); print; exit }'
}

expect_status() {
  local path="$1" expected="$2" actual
  shift 2
  actual="$(status_of "$path" "$@")"
  if [[ " $expected " == *" $actual "* ]]; then
    printf 'ok    %-34s %s\n' "$path" "$actual"
  else
    printf 'FAIL  %-34s got %s, expected %s\n' "$path" "$actual" "$expected"
    FAILURES=$((FAILURES + 1))
  fi
}

expect_header() {
  local path="$1" name="$2" expected="$3" actual
  actual="$(header_of "$path" "$name")"
  if [[ "$actual" == $expected ]]; then
    printf 'ok    %-34s %s\n' "$path $name" "${actual:0:60}"
  else
    printf 'FAIL  %-34s got "%s", expected "%s"\n' "$path $name" "$actual" "$expected"
    FAILURES=$((FAILURES + 1))
  fi
}

expect_no_header() {
  local path="$1" name="$2" actual
  actual="$(header_of "$path" "$name")"
  if [[ -z "$actual" ]]; then
    printf 'ok    %-34s absent\n' "$path $name"
  else
    printf 'FAIL  %-34s should be absent, got "%s"\n' "$path $name" "$actual"
    FAILURES=$((FAILURES + 1))
  fi
}

echo "== pages"
expect_status / 200
expect_status /products 200
expect_status /products/plum-jam 200
expect_status /account/orders/1 200
expect_status /robots.txt 200
expect_status /sitemap.xml 200
expect_status /api/health 200
expect_status /images/missing.png 404

echo "== files that must never be served"
expect_status /.env 403
expect_status /.git/config 403
expect_status /.htaccess 403
expect_status /logs/ 403
expect_status /logs/activity.log 403
expect_status /backend/app/config.py 403
expect_status /instance/jams.db 403
expect_status /jams.db 403
expect_status /jams.sqlite 403
expect_status /settings.ini 403
expect_status /index.html.bak 403
expect_status /wsgi.py 403
expect_status /assets/ 403

echo "== uploads"
expect_status /uploads/ 403
expect_status /uploads/.htaccess 403
expect_status /uploads/shell.php 403
expect_status /uploads/shell.php.webp 403
expect_status /uploads/photo.jpg 403
if [[ -n "$UPLOAD_NAME" ]]; then
  expect_status "/uploads/$UPLOAD_NAME" 200
  expect_header "/uploads/$UPLOAD_NAME" Content-Type "image/webp"
  expect_header "/uploads/$UPLOAD_NAME" X-Content-Type-Options "nosniff"
fi

echo "== request size and methods"
expect_status /api/contact 413 -X POST -H "Content-Type: application/json" --data-binary @<(head -c 13000000 /dev/zero)
expect_status / 405 -X TRACE

echo "== headers"
expect_header / X-Frame-Options "DENY"
expect_header / X-Content-Type-Options "nosniff"
expect_header / Referrer-Policy "strict-origin-when-cross-origin"
expect_header / Cross-Origin-Opener-Policy "same-origin"
expect_header / Permissions-Policy "camera=()*"
expect_header / Content-Security-Policy "default-src 'self'*frame-ancestors 'none'*"
expect_header /api/health Content-Security-Policy "default-src 'none'*"
expect_header /api/health X-Frame-Options "DENY"
expect_header / Server "Apache"
expect_no_header / X-Powered-By
if [[ "$BASE" == https://* ]]; then
  expect_header / Strict-Transport-Security "max-age=31536000*"
fi

echo
if [[ "$FAILURES" -eq 0 ]]; then
  echo "All Apache checks passed."
else
  echo "$FAILURES Apache check(s) failed."
  exit 1
fi
