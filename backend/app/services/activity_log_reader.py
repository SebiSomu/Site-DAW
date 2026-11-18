import os
import re
from dataclasses import dataclass
from datetime import date, datetime

from app.services.activity_logger import LOG_BACKUP_COUNT

LOG_LINE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| (?P<level>[A-Z]+) \| (?P<ip>[^|]*?) \| "
    r"(?P<user_id>[^|]*?) \| (?P<action>[a-z_]+) \| ?(?P<details>.*)$"
)
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S,%f"


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    level: str
    ip: str
    user_id: int | None
    action: str
    details: str


@dataclass(frozen=True)
class LogFilter:
    user_id: int | None = None
    action: str | None = None
    level: str | None = None
    date_from: date | None = None
    date_to: date | None = None

    def matches(self, entry: LogEntry) -> bool:
        day = entry.timestamp.date()
        return (
            (self.user_id is None or entry.user_id == self.user_id)
            and (self.action is None or entry.action == self.action)
            and (self.level is None or entry.level == self.level)
            and (self.date_from is None or day >= self.date_from)
            and (self.date_to is None or day <= self.date_to)
        )


@dataclass(frozen=True)
class LogPage:
    entries: list[LogEntry]
    total: int
    page: int
    per_page: int
    actions: list[str]


def parse_line(line: str) -> LogEntry | None:
    match = LOG_LINE.match(line.rstrip("\r\n"))
    if match is None:
        return None
    try:
        timestamp = datetime.strptime(match["timestamp"], TIMESTAMP_FORMAT)
    except ValueError:
        return None
    user_id = match["user_id"].strip()
    return LogEntry(
        timestamp=timestamp,
        level=match["level"],
        ip=match["ip"].strip(),
        user_id=int(user_id) if user_id.isdigit() else None,
        action=match["action"],
        details=match["details"],
    )


class ActivityLogReader:
    def __init__(self, path: str, backup_count: int = LOG_BACKUP_COUNT) -> None:
        self.path = path
        self.backup_count = backup_count

    def newest_first(self) -> list[LogEntry]:
        entries: list[LogEntry] = []
        for path in self._files_newest_first():
            with open(path, encoding="utf-8", errors="replace") as log_file:
                lines = log_file.readlines()
            entries.extend(entry for entry in map(parse_line, reversed(lines)) if entry is not None)
        return entries

    def search(self, log_filter: LogFilter, page: int, per_page: int) -> LogPage:
        entries = self.newest_first()
        matching = [entry for entry in entries if log_filter.matches(entry)]
        start = (page - 1) * per_page
        return LogPage(
            entries=matching[start : start + per_page],
            total=len(matching),
            page=page,
            per_page=per_page,
            actions=sorted({entry.action for entry in entries}),
        )

    def _files_newest_first(self) -> list[str]:
        candidates = [self.path, *(f"{self.path}.{number}" for number in range(1, self.backup_count + 1))]
        return [path for path in candidates if os.path.isfile(path)]
