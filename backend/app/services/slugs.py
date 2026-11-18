import re
import unicodedata

MAX_SLUG_LENGTH = 140
NOT_SLUG_CHARACTERS = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = NOT_SLUG_CHARACTERS.sub("-", ascii_text.lower()).strip("-")
    return slug[:MAX_SLUG_LENGTH].rstrip("-")
