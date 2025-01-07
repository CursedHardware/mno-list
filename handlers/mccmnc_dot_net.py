import requests

from .database import *
from .plmn import PLMN
from .utils import clean_space


def fetch(session: requests.Session):
    db.drop_tables([CarrierDotNet])
    db.create_tables([CarrierDotNet])
    with db.atomic():
        CarrierDotNet.bulk_create(make_carrier_list(session), batch_size=100)


def make_carrier_list(session: requests.Session):
    response = session.get("https://mcc-mnc.net/mcc-mnc.json")
    response.raise_for_status()
    records: list[dict[str, str]] = [
        {clean_space(name).lower(): clean_space(value) for name, value in row.items() if len(value) > 0}
        for row in response.json()
    ]
    for record in records:
        for iso_code in record["iso"].split("/"):
            yield CarrierDotNet(
                brand=record.get("brand"),
                operator=record.get("operator"),
                iso_code=iso_code,
                plmn=PLMN.from_tuple(record["mcc"], record["mnc"]),
            )
