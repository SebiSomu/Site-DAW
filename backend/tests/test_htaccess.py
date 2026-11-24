import re

import pytest

from app.config import BaseConfig
from app.security.headers import CSP, HSTS, HEADERS_FILE, HeaderPolicy
from app.services.uploads.storage import STORED_NAME

REPO_ROOT = HEADERS_FILE.parent
ROOT_HTACCESS = REPO_ROOT / "public" / ".htaccess"
UPLOADS_HTACCESS = REPO_ROOT / "backend" / "uploads" / ".htaccess"
VHOST = REPO_ROOT / "deploy" / "apache" / "mums-jams.conf"
HEADER_LINE = re.compile(r'^\s*Header always set (\S+) "([^"]*)"(?: "expr=%\{HTTPS\} (==|!=) \'on\'")?\s*$')


def read(path) -> str:
    return path.read_text(encoding="utf-8")


def root_headers() -> list[tuple[str, str, str | None]]:
    found = []
    for line in read(ROOT_HTACCESS).splitlines():
        match = HEADER_LINE.match(line)
        if match:
            name, value, condition = match.groups()
            https = None if condition is None else condition == "=="
            found.append((name, value, https))
    return found


def limit_request_body(path) -> int:
    return int(re.search(r"^\s*LimitRequestBody (\d+)\s*$", read(path), re.MULTILINE).group(1))


@pytest.fixture()
def policy() -> HeaderPolicy:
    return HeaderPolicy.load()


def test_root_htaccess_sends_every_common_header(policy):
    sent = {name: value for name, value, https in root_headers() if https is None}

    assert sent == policy.common


def test_root_htaccess_csp_matches_the_shared_policy(policy):
    csp = {https: value for name, value, https in root_headers() if name == CSP}

    assert csp == {True: policy.site_csp(https=True), False: policy.site_csp(https=False)}


def test_hsts_only_over_https(policy):
    hsts = [(value, https) for name, value, https in root_headers() if name == HSTS]

    assert hsts == [(policy.hsts, True)]


def test_apache_body_limit_matches_flask():
    assert limit_request_body(ROOT_HTACCESS) == BaseConfig.MAX_CONTENT_LENGTH
    assert limit_request_body(VHOST) == BaseConfig.MAX_CONTENT_LENGTH


def test_uploads_serve_only_names_the_app_creates():
    uploads = read(UPLOADS_HTACCESS)
    allowed = re.findall(r'<FilesMatch "([^"]+)">', uploads)

    assert allowed == [STORED_NAME.pattern]
    assert re.search(r"^Require all denied$", uploads, re.MULTILINE)
    assert "SetHandler none" in uploads
    assert "php_flag engine off" in uploads
    assert "Options -Indexes -ExecCGI" in uploads


@pytest.mark.parametrize("pattern", [r"\(\^\|/\)\\\.", r"log\|db\|sqlite", r"\^\(logs\|backend\|instance"])
def test_root_htaccess_denies_private_files(pattern):
    assert re.search(pattern, read(ROOT_HTACCESS))


def test_vhost_runs_one_process_so_in_memory_rate_limits_are_exact():
    assert re.search(r"WSGIDaemonProcess mums-jams processes=1 ", read(VHOST))
    assert BaseConfig.RATELIMIT_STORAGE_URI == "memory://"


def test_vhost_lets_htaccess_files_apply():
    assert read(VHOST).count("AllowOverride All") == 2
