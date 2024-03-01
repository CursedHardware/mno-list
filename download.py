#!/usr/bin/env python3
import csv
import dataclasses
import json
from typing import Iterable

import requests
from lxml.etree import HTML

DATASOURCE_URL = "https://mcc-mnc.com"


@dataclasses.dataclass
class Record:
    mcc: str
    mnc: str
    iso: str
    country: str
    country_code: str
    network: str


def get_records() -> Iterable[Record]:
    response = requests.get(DATASOURCE_URL)
    response.raise_for_status()
    text = response.text
    text = text[text.index("<tbody>"): text.index("</tbody>") + len("</tbody>")]
    for row in HTML(text).find("body/tbody"):
        record = Record(*[str(column.text).strip() for column in row])
        record.iso = record.iso.upper()
        yield record


def main():
    print("Downloading")
    records = sorted(get_records(), key=lambda _: (
        int(_.country_code) if _.country_code.isdigit() else 9999,
        _.iso,
        int(_.mcc),
        int(_.mnc),
        _.network,
    ))
    print("Downloaded")
    with open("carriers.csv", "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(_.name for _ in dataclasses.fields(Record))
        writer.writerows(map(dataclasses.astuple, records))
    with open("carriers.json", "w") as fp:
        json.dump(list(map(dataclasses.asdict, records)), fp, indent=2)


if __name__ == "__main__":
    main()
