import io
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from PIL import Image, UnidentifiedImageError

from app.errors import UploadError, UploadTooLargeError
from app.services.uploads.image_markers import image_end

ALLOWED_EXTENSIONS: dict[str, str] = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
MAX_PIXELS = 40_000_000
MIN_SIDE = 200


@dataclass(frozen=True)
class UploadCandidate:
    filename: str
    data: bytes

    @property
    def extension(self) -> str:
        return os.path.splitext(self.filename)[1].lower()


class FileValidator(ABC):
    reason: str

    @abstractmethod
    def validate(self, upload: UploadCandidate) -> None: ...


class SizeValidator(FileValidator):
    reason = "size"

    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes

    def validate(self, upload: UploadCandidate) -> None:
        if not upload.data:
            raise UploadError("This file is empty.")
        if len(upload.data) > self.max_bytes:
            raise UploadTooLargeError()


class ExtensionValidator(FileValidator):
    reason = "extension"

    def validate(self, upload: UploadCandidate) -> None:
        if upload.extension not in ALLOWED_EXTENSIONS:
            raise UploadError("Only .jpg, .jpeg, .png and .webp photos can be uploaded.")


class ImageFormatValidator(FileValidator):
    reason = "format"

    def validate(self, upload: UploadCandidate) -> None:
        expected = ALLOWED_EXTENSIONS[upload.extension]
        try:
            with Image.open(io.BytesIO(upload.data)) as image:
                actual = image.format
                width, height = image.size
                if width * height > MAX_PIXELS:
                    raise UploadError("This photo is too large in pixels. Please resize it below 40 megapixels.")
                image.verify()
            with Image.open(io.BytesIO(upload.data)) as image:
                image.load()
        except UploadError:
            raise
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError, ValueError) as error:
            raise UploadError("This file is not a real photo, or it is damaged.") from error
        if actual != expected:
            raise UploadError("The file name says one image type, but the file is another. Please save it again.")
        if min(width, height) < MIN_SIDE:
            raise UploadError(f"This photo is too small. It needs to be at least {MIN_SIDE} pixels on each side.")


class TrailingDataValidator(FileValidator):
    reason = "trailing_data"

    def validate(self, upload: UploadCandidate) -> None:
        end = image_end(ALLOWED_EXTENSIONS[upload.extension], upload.data)
        if end is None:
            raise UploadError("This file is not a real photo, or it is damaged.")
        if end != len(upload.data):
            raise UploadError(
                "This photo has extra data hidden after the picture. Please export it again as a plain photo."
            )


def default_validators(max_bytes: int) -> list[FileValidator]:
    return [SizeValidator(max_bytes), ExtensionValidator(), ImageFormatValidator(), TrailingDataValidator()]
