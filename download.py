#!/usr/bin/env python3
import csv
import dataclasses
import json
from typing import Iterable, Optional

import requests
from lxml.etree import HTML

DATASOURCE_URL = "https://mcc-mnc.com"


@dataclasses.dataclass
class Record:
    mcc: str
    mnc: str
    iso: Optional[str]
    country: str
    country_code: Optional[str]
    network: str


def get_records() -> Iterable[Record]:
    response = requests.get(DATASOURCE_URL)
    response.raise_for_status()
    text = response.text
    text = text[text.index("<tbody>"): text.index("</tbody>") + len("</tbody>")]
    for row in HTML(text).find("body/tbody"):
        fields = [column.text for column in row]
        iso = fields[2].upper()
        yield Record(
            mcc=fields[0],
            mnc=fields[1],
            iso=iso if iso != "N/A" else None,
            country=fields[3],
            country_code=fields[4],
            network=fields[5],
        )


def main():
    print("Downloading")
    records = list(get_records())
    print("Downloaded")
    with open("carriers.csv", "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(_.name for _ in dataclasses.fields(Record))
        writer.writerows(map(dataclasses.astuple, records))
    with open("npm/carriers.json", "w") as fp:
        json.dump(list(map(dataclasses.asdict, records)), fp, indent=2, skipkeys=True)


if __name__ == "__main__":
    main()
