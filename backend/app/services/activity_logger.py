import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, has_request_context, request
from flask_login import current_user

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(ip)s | %(user_id)s | %(action)s | %(details)s"
MAX_LOG_BYTES = 1024 * 1024
LOG_BACKUP_COUNT = 5


class ActivityLogger:
    def __init__(self) -> None:
        self._logger = logging.getLogger("activity")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

    def init_app(self, app: Flask) -> None:
        path = app.config["ACTIVITY_LOG_PATH"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        for handler in list(self._logger.handlers):
            self._logger.removeHandler(handler)
            handler.close()
        handler = RotatingFileHandler(
            path, maxBytes=MAX_LOG_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8", delay=True
        )
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        self._logger.addHandler(handler)

    def info(self, action: str, details: str = "") -> None:
        self._write(logging.INFO, action, details)

    def warning(self, action: str, details: str = "") -> None:
        self._write(logging.WARNING, action, details)

    def _write(self, level: int, action: str, details: str) -> None:
        in_request = has_request_context()
        context = {
            "ip": request.remote_addr if in_request else "-",
            "user_id": current_user.get_id() if in_request and current_user.is_authenticated else "-",
            "action": action,
            "details": " ".join(str(details).split()),
        }
        self._logger.log(level, action, extra=context)


activity_logger = ActivityLogger()
