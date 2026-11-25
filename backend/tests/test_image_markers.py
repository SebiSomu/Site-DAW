import io

import pytest
from PIL import Image

from app.services.uploads.image_markers import PNG_SIGNATURE, image_end, jpeg_end, png_end, webp_end


def encoded(image_format: str) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (240, 240), (139, 45, 58)).save(output, image_format)
    return output.getvalue()


JPEG = encoded("JPEG")
PNG = encoded("PNG")
WEBP = encoded("WEBP")


@pytest.mark.parametrize(
    "data",
    [
        b"\xff\xd8",
        b"\xff\xd8\x00",
        b"\xff\xd8\xff\xff\xff",
        b"\xff\xd8\xff\xe0\x00",
        b"\xff\xd8\xff\xe0\x00\x01",
        b"\xff\xd8\xff\xda\x00\x02\x11\x22\x33",
    ],
    ids=["no-segments", "not-a-marker", "only-fill-bytes", "cut-length", "length-below-two", "scan-never-ends"],
)
def test_broken_jpeg_structures_have_no_end(data):
    assert jpeg_end(data) is None


def test_jpeg_standalone_and_restart_markers_are_stepped_over():
    data = b"\xff\xd8\xff\x01\xff\xda\x00\x02\x11\xff\x00\x22\xff\xd0\x33\xff\xd9"

    assert jpeg_end(data) == len(data)


def test_jpeg_end_ignores_bytes_after_the_end_marker():
    assert jpeg_end(JPEG + b"PK\x03\x04") == len(JPEG)


def test_jpeg_cut_before_the_end_marker_has_no_end():
    assert jpeg_end(JPEG[:-2]) is None


@pytest.mark.parametrize(
    "data",
    [b"", b"\x89PNG", PNG_SIGNATURE, PNG_SIGNATURE + b"\x00\x00\x10\x00IHDR", PNG[:-1]],
    ids=["empty", "cut-signature", "signature-only", "chunk-longer-than-file", "cut-iend"],
)
def test_broken_png_structures_have_no_end(data):
    assert png_end(data) is None


def test_png_end_ignores_bytes_after_iend():
    assert png_end(PNG + b"<?php echo 1; ?>") == len(PNG)


@pytest.mark.parametrize(
    "data",
    [b"RIFF", b"RIFF\x00\x00\x00\x00WAVE", b"RIFX" + WEBP[4:], WEBP[:4] + (len(WEBP)).to_bytes(4, "little") + WEBP[8:]],
    ids=["too-short", "not-webp", "wrong-magic", "size-past-the-end"],
)
def test_broken_webp_structures_have_no_end(data):
    assert webp_end(data) is None


def test_odd_sized_webp_includes_its_padding_byte():
    body = b"WEBP" + b"VP8L" + (1).to_bytes(4, "little") + b"\x00"
    data = b"RIFF" + len(body).to_bytes(4, "little") + body + b"\x00"

    assert len(body) % 2 == 1
    assert webp_end(data) == len(data)


def test_image_end_dispatches_by_format_and_knows_only_allowed_formats():
    assert image_end("JPEG", JPEG) == len(JPEG)
    assert image_end("PNG", PNG) == len(PNG)
    assert image_end("WEBP", WEBP) == len(WEBP)
    assert image_end("GIF", b"GIF89a") is None
