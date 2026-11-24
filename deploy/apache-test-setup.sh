#!/usr/bin/env bash
set -euo pipefail

if [[ "${CI:-}" != "true" && "${ALLOW_APACHE_TEST_SETUP:-}" != "1" ]]; then
  echo "This builds a throwaway test server in /srv/mums-jams and deletes what is there."
  echo "It runs only in CI, or with ALLOW_APACHE_TEST_SETUP=1. Never run it on the live VM."
  exit 1
fi

REPO="$(cd "${1:-.}" && pwd)"
APP_ROOT=/srv/mums-jams
UPLOAD_NAME=0123456789abcdef0123456789abcdef.webp
WSGI_PYTHON="/usr/bin/$(ldd /usr/lib/apache2/modules/mod_wsgi.so | grep -o 'libpython3\.[0-9]*' | head -n 1 | sed 's/^lib//')"

sudo rm -rf "$APP_ROOT"
sudo mkdir -p "$APP_ROOT/backend/uploads" "$APP_ROOT/backend/logs" "$APP_ROOT/backend/instance"
sudo cp -r "$REPO/dist" "$APP_ROOT/dist"
sudo cp -r "$REPO/backend/app" "$REPO/backend/migrations" "$REPO/backend/wsgi.py" "$REPO/backend/requirements.txt" "$APP_ROOT/backend/"
sudo cp "$REPO/backend/uploads/.htaccess" "$APP_ROOT/backend/uploads/.htaccess"
sudo cp "$REPO/security-headers.json" "$APP_ROOT/security-headers.json"

sudo "$WSGI_PYTHON" -m venv "$APP_ROOT/backend/.venv"
sudo "$APP_ROOT/backend/.venv/bin/pip" install -q -r "$APP_ROOT/backend/requirements.txt"

sudo tee "$APP_ROOT/backend/.env" > /dev/null <<ENV
FLASK_CONFIG=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:///$APP_ROOT/backend/instance/jams.db
ADMIN_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')
STRIPE_SECRET_KEY=sk_test_apache_check
STRIPE_WEBHOOK_SECRET=whsec_apache_check
SITE_URL=http://localhost
TURNSTILE_SITE_KEY=1x00000000000000000000AA
TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA
ENV
sudo chmod 640 "$APP_ROOT/backend/.env"

(cd "$APP_ROOT/backend" && sudo env FLASK_APP=wsgi.py .venv/bin/flask db upgrade > /dev/null)

printf '<?php echo "executed"; ?>' | sudo tee "$APP_ROOT/backend/uploads/shell.php" > /dev/null
printf 'GIF89a<?php echo "executed"; ?>' | sudo tee "$APP_ROOT/backend/uploads/shell.php.webp" > /dev/null
printf 'not a photo' | sudo tee "$APP_ROOT/backend/uploads/photo.jpg" > /dev/null
"$APP_ROOT/backend/.venv/bin/python" -c "from PIL import Image; Image.new('RGB', (200, 200), (139, 45, 58)).save('/tmp/$UPLOAD_NAME', 'WEBP')"
sudo cp "/tmp/$UPLOAD_NAME" "$APP_ROOT/backend/uploads/$UPLOAD_NAME"

sudo chown -R root:www-data "$APP_ROOT"
sudo chmod -R g+rX,o-rwx "$APP_ROOT"
sudo chown -R www-data:www-data "$APP_ROOT/backend/uploads" "$APP_ROOT/backend/logs" "$APP_ROOT/backend/instance"

sudo cp "$REPO/deploy/apache/security.conf" /etc/apache2/conf-available/zz-mums-jams-security.conf
sudo cp "$REPO/deploy/apache/mums-jams.conf" /etc/apache2/sites-available/mums-jams.conf
sudo a2enmod -q headers rewrite wsgi > /dev/null
sudo a2enconf -q zz-mums-jams-security > /dev/null
sudo a2dissite -q 000-default > /dev/null
sudo a2ensite -q mums-jams > /dev/null
sudo apache2ctl configtest
sudo apache2ctl restart || sudo service apache2 restart

echo "$UPLOAD_NAME"
