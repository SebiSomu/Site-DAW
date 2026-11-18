PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_START = b"\xff\xd8"
JPEG_END_MARKER = 0xD9
JPEG_SCAN_MARKER = 0xDA
JPEG_STANDALONE_MARKERS = frozenset({0x01, *range(0xD0, 0xD8)})


def _is_scan_boundary(data: bytes, index: int) -> bool:
    following = data[index + 1]
    return data[index] == 0xFF and following != 0x00 and following not in JPEG_STANDALONE_MARKERS


def _skip_scan(data: bytes, index: int) -> int | None:
    while index < len(data) - 1:
        if _is_scan_boundary(data, index):
            return index
        index += 1
    return None


def jpeg_end(data: bytes) -> int | None:
    if not data.startswith(JPEG_START):
        return None
    index = len(JPEG_START)
    while index < len(data):
        if data[index] != 0xFF:
            return None
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            return None
        marker = data[index]
        index += 1
        if marker == JPEG_END_MARKER:
            return index
        if marker in JPEG_STANDALONE_MARKERS:
            continue
        if index + 2 > len(data):
            return None
        length = int.from_bytes(data[index : index + 2], "big")
        if length < 2:
            return None
        index += length
        if marker == JPEG_SCAN_MARKER:
            index = _skip_scan(data, index)
            if index is None:
                return None
    return None


def png_end(data: bytes) -> int | None:
    if not data.startswith(PNG_SIGNATURE):
        return None
    index = len(PNG_SIGNATURE)
    while index + 8 <= len(data):
        length = int.from_bytes(data[index : index + 4], "big")
        chunk_type = data[index + 4 : index + 8]
        index += 12 + length
        if index > len(data):
            return None
        if chunk_type == b"IEND":
            return index
    return None


def webp_end(data: bytes) -> int | None:
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    size = int.from_bytes(data[4:8], "little")
    end = 8 + size + (size % 2)
    return end if end <= len(data) else None


END_FINDERS = {"JPEG": jpeg_end, "PNG": png_end, "WEBP": webp_end}


def image_end(image_format: str, data: bytes) -> int | None:
    finder = END_FINDERS.get(image_format)
    return finder(data) if finder else None
