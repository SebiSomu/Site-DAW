import io
import os

import pytest
from PIL import Image

from app.errors import UploadError, UploadTooLargeError
from app.services.uploads import ImageUploadPipeline, UploadCandidate, UploadStorage
from app.services.uploads.image_markers import jpeg_end, png_end, webp_end

SECRET = b"PK\x03\x04hidden-payload-secret"
TWELVE_MB = 12 * 1024 * 1024


def picture(size=(800, 600), mode="RGB", colour=(180, 40, 60)):
    image = Image.new(mode, size, colour if mode == "RGB" else (*colour, 128))
    for x in range(0, size[0], 7):
        image.putpixel((x, x % size[1]), (10, 200, 90) if mode == "RGB" else (10, 200, 90, 255))
    return image


def encode(image, image_format, **options):
    output = io.BytesIO()
    image.save(output, image_format, **options)
    return output.getvalue()


def jpeg_with_exif(size=(800, 600), orientation=1):
    exif = Image.Exif()
    exif[0x013B] = "Secret Photographer"
    exif[0x0112] = orientation
    return encode(picture(size), "JPEG", exif=exif.tobytes(), quality=90)


@pytest.fixture()
def pipeline(app):
    return ImageUploadPipeline()


def stored_image(app, filename):
    return Image.open(os.path.join(app.config["UPLOAD_FOLDER"], filename))


def stored_files(app):
    folder = app.config["UPLOAD_FOLDER"]
    return os.listdir(folder) if os.path.isdir(folder) else []


def test_clean_photo_is_re_encoded_to_webp_without_metadata(app, pipeline, activity_log):
    filename = pipeline.store(UploadCandidate("jar.jpg", jpeg_with_exif()))

    assert UploadStorage.is_stored_name(filename)
    with stored_image(app, filename) as image:
        assert image.format == "WEBP"
        assert image.size == (800, 600)
        assert not image.getexif()
        assert "icc_profile" not in image.info
    with open(os.path.join(app.config["UPLOAD_FOLDER"], filename), "rb") as file:
        assert b"Secret Photographer" not in file.read()
    assert "image_stored" in activity_log()


def test_large_photo_is_scaled_down(app, pipeline):
    filename = pipeline.store(UploadCandidate("big.png", encode(picture((3200, 2000)), "PNG")))

    with stored_image(app, filename) as image:
        assert max(image.size) == 1600


def test_camera_rotation_is_applied_before_the_metadata_is_dropped(app, pipeline):
    filename = pipeline.store(UploadCandidate("sideways.jpeg", jpeg_with_exif((600, 400), orientation=6)))

    with stored_image(app, filename) as image:
        assert image.size == (400, 600)


def test_transparent_png_keeps_its_transparency(app, pipeline):
    filename = pipeline.store(UploadCandidate("label.png", encode(picture(mode="RGBA"), "PNG")))

    with stored_image(app, filename) as image:
        assert image.mode == "RGBA"


@pytest.mark.parametrize(
    ("name", "data"),
    [
        ("progressive.jpg", encode(picture(), "JPEG", progressive=True)),
        ("photo.webp", encode(picture(), "WEBP", quality=80)),
        ("UPPER.JPG", encode(picture(), "JPEG")),
    ],
)
def test_every_allowed_kind_of_photo_is_accepted(app, pipeline, name, data):
    assert UploadStorage.is_stored_name(pipeline.store(UploadCandidate(name, data)))


@pytest.mark.parametrize(
    ("name", "data"),
    [
        ("jar.jpg", encode(picture(), "JPEG") + SECRET),
        ("jar.png", encode(picture(), "PNG") + SECRET),
        ("jar.webp", encode(picture(), "WEBP") + SECRET),
        ("jar.jpg", encode(picture(), "JPEG") + b"\x00" * 16),
    ],
)
def test_photo_with_data_hidden_after_the_picture_is_rejected(app, pipeline, activity_log, name, data):
    with pytest.raises(UploadError, match="extra data hidden"):
        pipeline.store(UploadCandidate(name, data))

    assert "upload_rejected" in activity_log()
    assert "reason=trailing_data" in activity_log()
    assert stored_files(app) == []


def test_text_chunk_inside_a_png_does_not_survive(app, pipeline):
    from PIL.PngImagePlugin import PngInfo

    info = PngInfo()
    info.add_text("Comment", "secret-message-in-metadata")
    filename = pipeline.store(UploadCandidate("jar.png", encode(picture(), "PNG", pnginfo=info)))

    with open(os.path.join(app.config["UPLOAD_FOLDER"], filename), "rb") as file:
        assert b"secret-message-in-metadata" not in file.read()


def test_re_encoding_changes_the_pixels_that_could_carry_a_hidden_message(app, pipeline):
    original = picture((400, 300))
    payload = original.copy()
    for x in range(400):
        red, green, blue = payload.getpixel((x, 0))
        payload.putpixel((x, 0), (red ^ 1, green, blue))
    filename = pipeline.store(UploadCandidate("lsb.png", encode(payload, "PNG")))

    with stored_image(app, filename) as image:
        stored_row = [image.convert("RGB").getpixel((x, 0)) for x in range(400)]
    assert stored_row != [payload.getpixel((x, 0)) for x in range(400)]


@pytest.mark.parametrize("name", ["virus.exe", "shell.php", "jar.gif", "jar.svg", "jar", "jar.jpg.php", ".htaccess"])
def test_disallowed_extension_is_rejected(app, pipeline, activity_log, name):
    with pytest.raises(UploadError, match="Only .jpg, .jpeg, .png and .webp"):
        pipeline.store(UploadCandidate(name, encode(picture(), "JPEG")))

    assert "reason=extension" in activity_log()


@pytest.mark.parametrize(
    "data",
    [
        b"<?php system($_GET['c']); ?>",
        b"GIF89a fake header",
        encode(picture(), "JPEG")[:2000],
    ],
)
def test_file_that_is_not_a_real_photo_is_rejected(app, pipeline, activity_log, data):
    with pytest.raises(UploadError, match="not a real photo"):
        pipeline.store(UploadCandidate("jar.jpg", data))

    assert "reason=format" in activity_log()


def test_photo_whose_name_lies_about_its_type_is_rejected(app, pipeline):
    with pytest.raises(UploadError, match="file name says one image type"):
        pipeline.store(UploadCandidate("jar.jpg", encode(picture(), "PNG")))


def test_tiny_photo_is_rejected(app, pipeline):
    with pytest.raises(UploadError, match="too small"):
        pipeline.store(UploadCandidate("jar.png", encode(picture((50, 50)), "PNG")))


def test_empty_file_is_rejected(app, pipeline):
    with pytest.raises(UploadError, match="empty"):
        pipeline.store(UploadCandidate("jar.jpg", b""))


def test_file_over_12_mb_is_rejected_with_413(app, pipeline, activity_log):
    with pytest.raises(UploadTooLargeError) as raised:
        pipeline.store(UploadCandidate("jar.jpg", b"\xff" * (TWELVE_MB + 1)))

    assert raised.value.status_code == 413
    assert "reason=size" in activity_log()


@pytest.fixture()
def upload_route(app):
    @app.post("/api/test/upload")
    def test_upload():
        from flask import jsonify, request

        filename = ImageUploadPipeline().store_file(request.files.get("photo"))
        return jsonify(filename=filename), 201

    return app.test_client()


def send_photo(client, name, data):
    token = client.get("/api/csrf").get_json()["csrf_token"]
    return client.post(
        "/api/test/upload",
        data={"photo": (io.BytesIO(data), name)},
        headers={"X-CSRFToken": token},
        content_type="multipart/form-data",
    )


def test_request_over_12_mb_is_refused_before_it_is_read(upload_route, activity_log):
    response = send_photo(upload_route, "jar.jpg", b"\xff" * (13 * 1024 * 1024))

    assert response.status_code == 413
    assert response.get_json() == {"error": "This file is larger than 12 MB. Please choose a smaller photo."}
    assert "reason=too_large" in activity_log()


def test_upload_without_a_csrf_token_is_refused(upload_route):
    response = upload_route.post(
        "/api/test/upload", data={"photo": (io.BytesIO(encode(picture(), "JPEG")), "jar.jpg")}
    )

    assert response.status_code == 400


def test_upload_rejection_comes_back_as_a_clear_json_error(upload_route):
    response = send_photo(upload_route, "shell.php", b"<?php ?>")

    assert response.status_code == 400
    assert "Only .jpg" in response.get_json()["error"]


def test_missing_file_is_a_clear_error(upload_route):
    token = upload_route.get("/api/csrf").get_json()["csrf_token"]
    response = upload_route.post("/api/test/upload", data={}, headers={"X-CSRFToken": token})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Please choose a photo to upload."}


def test_stored_photo_is_served_as_an_image_only(upload_route):
    filename = send_photo(upload_route, "jar.jpg", encode(picture(), "JPEG")).get_json()["filename"]

    response = upload_route.get(f"/uploads/{filename}")

    assert response.status_code == 200
    assert response.mimetype == "image/webp"
    assert response.headers["X-Content-Type-Options"] == "nosniff"


@pytest.mark.parametrize("path", ["/uploads/shell.php", "/uploads/..%2Factivity.log", "/uploads/ABC.webp", "/uploads/.htaccess"])
def test_uploads_route_serves_nothing_but_stored_photos(upload_route, path):
    assert upload_route.get(path).status_code == 404


def test_deleting_ignores_names_that_are_not_stored_photos(tmp_path):
    secret = tmp_path / "keep.txt"
    secret.write_text("keep me")
    storage = UploadStorage(str(tmp_path / "uploads"))

    storage.delete("../keep.txt")

    assert secret.exists()


def test_end_markers_are_found_exactly():
    jpeg = encode(picture(), "JPEG")
    png = encode(picture(), "PNG")
    webp = encode(picture(), "WEBP")

    assert (jpeg_end(jpeg), png_end(png), webp_end(webp)) == (len(jpeg), len(png), len(webp))
    assert jpeg_end(b"not a jpeg") is None
    assert png_end(png[:-12]) is None
