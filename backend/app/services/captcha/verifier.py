from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CaptchaResult:
    success: bool
    error_codes: tuple[str, ...] = field(default_factory=tuple)


class CaptchaVerifier(ABC):
    @property
    @abstractmethod
    def site_key(self) -> str: ...

    @abstractmethod
    def verify(self, token: str, remote_ip: str | None) -> CaptchaResult: ...
