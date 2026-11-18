import io

from PIL import Image, ImageOps

MAX_SIDE = 1600
WEBP_QUALITY = 82


class ImageSanitizer:
    def __init__(self, max_side: int = MAX_SIDE, quality: int = WEBP_QUALITY) -> None:
        self.max_side = max_side
        self.quality = quality

    def clean(self, data: bytes) -> bytes:
        with Image.open(io.BytesIO(data)) as source:
            upright = ImageOps.exif_transpose(source)
            mode = "RGBA" if self._has_transparency(upright) else "RGB"
            converted = upright.convert(mode)
        converted.thumbnail((self.max_side, self.max_side), Image.Resampling.LANCZOS)
        pixels_only = Image.frombytes(converted.mode, converted.size, converted.tobytes())
        output = io.BytesIO()
        pixels_only.save(output, "WEBP", quality=self.quality, method=4)
        return output.getvalue()

    @staticmethod
    def _has_transparency(image: Image.Image) -> bool:
        return image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info)
