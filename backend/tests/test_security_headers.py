import re

import pytest

from app import create_app
from app.security.headers import HEADERS_FILE, SERVER_NAME, HeaderPolicy

REPO_ROOT = HEADERS_FILE.parent
EXPECTED = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
}


@pytest.fixture()
def policy() -> HeaderPolicy:
    return HeaderPolicy.load()


def directives(csp: str) -> dict[str, list[str]]:
    parsed = {}
    for directive in csp.split(";"):
        name, *sources = directive.split()
        parsed[name] = sources
    return parsed


@pytest.mark.parametrize("url", ["/api/health", "/api/csrf", "/api/does-not-exist", "/robots.txt"])
def test_every_response_carries_the_security_headers(api, url):
    response = api.get(url)

    for name, value in EXPECTED.items():
        assert response.headers[name] == value
    assert "camera=()" in response.headers["Permissions-Policy"]
    assert response.headers["Content-Security-Policy"].startswith("default-src 'none'")
    assert response.headers["Server"] == SERVER_NAME


def test_error_responses_carry_them_too(api):
    response = api.post("/api/auth/login", {"email": "not-an-email"})

    assert response.status_code == 400
    assert response.headers["X-Frame-Options"] == "DENY"


def test_api_policy_allows_nothing_to_load(policy):
    parsed = directives(policy.api_csp())

    assert parsed["default-src"] == ["'none'"]
    assert parsed["frame-ancestors"] == ["'none'"]


def test_hsts_only_over_https(api, tmp_path):
    assert "Strict-Transport-Security" not in api.get("/api/health").headers

    secure = create_app("testing", {"HTTPS_HEADERS": True, "ACTIVITY_LOG_PATH": str(tmp_path / "a.log")})
    headers = secure.test_client().get("/api/health").headers

    assert headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"


def test_production_turns_https_headers_on():
    from app.config import ProductionConfig

    assert ProductionConfig.HTTPS_HEADERS is True


def test_server_details_are_hidden(api):
    headers = api.get("/api/health").headers

    assert "Werkzeug" not in headers.get("Server", "")
    assert "Python" not in headers.get("Server", "")
    assert "X-Powered-By" not in headers


@pytest.mark.parametrize("https", [False, True])
def test_site_policy_is_strict(policy, https):
    csp = policy.site_csp(https)
    parsed = directives(csp)
    every_source = [source for sources in parsed.values() for source in sources]

    assert "'unsafe-inline'" not in every_source
    assert "'unsafe-eval'" not in every_source
    assert "*" not in every_source
    assert not any(source.startswith(("data:", "blob:", "http:")) for source in every_source)
    assert parsed["default-src"] == ["'self'"]
    assert parsed["object-src"] == ["'none'"]
    assert parsed["frame-ancestors"] == ["'none'"]
    assert parsed["base-uri"] == ["'self'"]
    assert parsed["form-action"] == ["'self'"]
    assert ("upgrade-insecure-requests" in parsed) is https


def test_only_turnstile_is_trusted_besides_our_own_origin(policy):
    outside = {
        source
        for sources in directives(policy.site_csp(True)).values()
        for source in sources
        if source.startswith("https://")
    }

    assert outside == {"https://challenges.cloudflare.com"}


def test_no_raw_html_rendering_in_the_frontend():
    offenders = [
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "src").rglob("*.svelte")
        if re.search(r"\{@html\b", path.read_text(encoding="utf-8"))
    ]

    assert offenders == []


def test_frontend_never_builds_code_from_strings():
    pattern = re.compile(r"\beval\(|new Function\(|\.innerHTML\s*=|insertAdjacentHTML\(")
    offenders = [
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "src").rglob("*")
        if path.suffix in {".ts", ".svelte"} and pattern.search(path.read_text(encoding="utf-8"))
    ]

    assert offenders == []
