import base64
import os
import re
from urllib.parse import urljoin

import requests

BASE_URL = "https://android.googlesource.com/platform/frameworks/opt/telephony/"
BRANCH = "HEAD"
FILEPATH = "src/java/com/android/internal/telephony/MccTable.java"

RE_MCC_ENTRY = re.compile(r'\(\s*(?P<mcc>\d{3}),\s*"(?P<iso>\w{2})",\s*(?P<n>\d)')


def fetch(session: requests.Session):
    response = session.get(
        url=urljoin(BASE_URL, os.path.join("+", BRANCH, FILEPATH)),
        params={"format": "TEXT"},
    )
    response.raise_for_status()
    codeblock = base64.decodebytes(response.content).decode("utf-8")

    entries = [
        {
            "mcc": entry.group("mcc"),
            "iso": entry.group("iso").upper(),
            "smallestDigitsMCC": int(entry.group("n")),
        }
        for entry in RE_MCC_ENTRY.finditer(codeblock)
    ]

    return sorted(entries, key=lambda _: int(_["mcc"]))
