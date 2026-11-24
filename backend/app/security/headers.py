import json
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, Response

from app.config import BACKEND_DIR

HEADERS_FILE = Path(BACKEND_DIR).parent / "security-headers.json"
SERVER_NAME = "mums-jams"
CSP = "Content-Security-Policy"
HSTS = "Strict-Transport-Security"


def join_directives(directives: list[str]) -> str:
    return "; ".join(directives)


@dataclass(frozen=True)
class HeaderPolicy:
    common: dict[str, str]
    site_directives: tuple[str, ...]
    api_directives: tuple[str, ...]
    hsts: str
    https_directive: str

    @classmethod
    def load(cls, path: Path = HEADERS_FILE) -> "HeaderPolicy":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            common=dict(raw["common"]),
            site_directives=tuple(raw["site_csp"]),
            api_directives=tuple(raw["api_csp"]),
            hsts=raw["https_only"]["Strict-Transport-Security"],
            https_directive=raw["https_only"]["csp_directive"],
        )

    def site_csp(self, https: bool) -> str:
        return join_directives([*self.site_directives, *([self.https_directive] if https else [])])

    def api_csp(self) -> str:
        return join_directives(list(self.api_directives))

    def api_headers(self, https: bool) -> dict[str, str]:
        headers = {**self.common, CSP: self.api_csp()}
        if https:
            headers[HSTS] = self.hsts
        return headers


class SecurityHeaders:
    def __init__(self, policy: HeaderPolicy | None = None) -> None:
        self._policy = policy

    def init_app(self, app: Flask) -> None:
        policy = self._policy or HeaderPolicy.load()
        headers = policy.api_headers(https=app.config["HTTPS_HEADERS"])

        @app.after_request
        def apply_security_headers(response: Response) -> Response:
            response.headers.update(headers)
            response.headers["Server"] = SERVER_NAME
            response.headers.pop("X-Powered-By", None)
            return response


security_headers = SecurityHeaders()
