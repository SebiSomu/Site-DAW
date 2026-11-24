from app.services.captcha.verifier import CaptchaResult, CaptchaVerifier

FAKE_CAPTCHA_TOKEN = "fake-captcha-pass"
FAKE_SITE_KEY = "fake-site-key"


class FakeVerifier(CaptchaVerifier):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    @property
    def site_key(self) -> str:
        return FAKE_SITE_KEY

    def verify(self, token: str, remote_ip: str | None) -> CaptchaResult:
        self.calls.append((token, remote_ip))
        if token == FAKE_CAPTCHA_TOKEN:
            return CaptchaResult(success=True)
        return CaptchaResult(success=False, error_codes=("invalid-input-response",))
