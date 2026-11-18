import os
import re
from uuid import uuid4

STORED_NAME = re.compile(r"^[0-9a-f]{32}\.webp$")


class UploadStorage:
    def __init__(self, folder: str) -> None:
        self.folder = folder

    def save(self, data: bytes) -> str:
        os.makedirs(self.folder, exist_ok=True)
        filename = f"{uuid4().hex}.webp"
        temporary = os.path.join(self.folder, f".{filename}.part")
        with open(temporary, "wb") as file:
            file.write(data)
        os.replace(temporary, self.path(filename))
        return filename

    def delete(self, filename: str) -> None:
        if self.is_stored_name(filename):
            try:
                os.remove(self.path(filename))
            except FileNotFoundError:
                pass

    def path(self, filename: str) -> str:
        return os.path.join(self.folder, filename)

    @staticmethod
    def is_stored_name(filename: str) -> bool:
        return bool(STORED_NAME.match(filename))
