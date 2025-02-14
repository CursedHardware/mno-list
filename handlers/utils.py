import bz2
import gzip
import json
import re
from pathlib import Path
from unicodedata import normalize

from .plmn import PLMN

RE_SPACE = re.compile(r"\s+")
RE_SPACE_LEFT_BRACKET = re.compile(r"\(\s+")
RE_SPACE_RIGHT_BRACKET = re.compile(r"\s+\)")


def clean_space(text: str) -> str | None:
    if text is None:
        return None
    text = normalize("NFKC", text)
    text = RE_SPACE.sub(chr(0x20), text)
    text = RE_SPACE_LEFT_BRACKET.sub(chr(0x28), text)
    text = RE_SPACE_RIGHT_BRACKET.sub(chr(0x29), text)
    return text.strip()


class CustomEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        if not kwargs["indent"]:
            kwargs["separators"] = (',', ':')
        super().__init__(*args, **kwargs)

    def default(self, o):
        if isinstance(o, PLMN):
            return o.mccmnc
        if isinstance(o, bytes):
            return o.hex()
        return super().default(o)


def emit_file(data: str | bytes, paths: list[Path]):
    data = data.encode("utf-8") if isinstance(data, str) else data
    for path in paths:
        if path.name.endswith(".gz"):
            path.write_bytes(gzip.compress(data, compresslevel=9))
        elif path.name.endswith(".bz2"):
            path.write_bytes(bz2.compress(data, compresslevel=9))
        else:
            path.write_bytes(data)
