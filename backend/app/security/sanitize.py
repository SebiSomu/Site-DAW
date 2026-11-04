from html import unescape

import nh3


def plain_text(value: str) -> str:
    return unescape(nh3.clean(value, tags=set())).strip()
