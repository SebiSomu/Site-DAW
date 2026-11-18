from flask import Blueprint, current_app, send_from_directory

from app.errors import NotFoundError
from app.services.uploads import UploadStorage

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.get("/uploads/<filename>")
def uploaded_image(filename: str):
    if not UploadStorage.is_stored_name(filename):
        raise NotFoundError()
    response = send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, mimetype="image/webp", max_age=86400)
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
