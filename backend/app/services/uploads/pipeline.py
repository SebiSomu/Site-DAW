from typing import Sequence

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.errors import UploadError
from app.services.activity_logger import activity_logger
from app.services.uploads.sanitizer import ImageSanitizer
from app.services.uploads.storage import UploadStorage
from app.services.uploads.validators import FileValidator, UploadCandidate, default_validators


def read_upload(file: FileStorage | None, max_bytes: int) -> UploadCandidate:
    if file is None or not file.filename:
        raise UploadError("Please choose a photo to upload.")
    return UploadCandidate(filename=file.filename, data=file.read(max_bytes + 1))


class ImageUploadPipeline:
    def __init__(
        self,
        validators: Sequence[FileValidator] | None = None,
        sanitizer: ImageSanitizer | None = None,
        storage: UploadStorage | None = None,
    ) -> None:
        self.max_bytes = current_app.config["MAX_UPLOAD_BYTES"]
        self.validators = list(validators) if validators is not None else default_validators(self.max_bytes)
        self.sanitizer = sanitizer or ImageSanitizer()
        self.storage = storage or UploadStorage(current_app.config["UPLOAD_FOLDER"])

    def store_file(self, file: FileStorage | None) -> str:
        return self.store(read_upload(file, self.max_bytes))

    def store(self, upload: UploadCandidate) -> str:
        for validator in self.validators:
            try:
                validator.validate(upload)
            except UploadError:
                activity_logger.warning("upload_rejected", f"reason={validator.reason} file={self._log_name(upload)}")
                raise
        cleaned = self.sanitizer.clean(upload.data)
        filename = self.storage.save(cleaned)
        activity_logger.info("image_stored", f"file={filename} from={self._log_name(upload)} bytes={len(cleaned)}")
        return filename

    @staticmethod
    def _log_name(upload: UploadCandidate) -> str:
        return secure_filename(upload.filename)[:80] or "-"
