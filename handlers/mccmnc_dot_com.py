import lxml.html
import requests

from .database import *
from .plmn import PLMN
from .utils import clean_space


def fetch(session: requests.Session):
    db.drop_tables([CarrierDotCom])
    db.create_tables([CarrierDotCom])
    with db.atomic():
        CarrierDotCom.bulk_create(make_carrier_list(session), batch_size=100)


def make_carrier_list(session: requests.Session):
    response = session.get("https://mcc-mnc.com")
    response.raise_for_status()
    parsed = lxml.html.fromstring(response.text)
    headers = [
        clean_space(header.text).lower()
        for header in parsed.xpath('//thead/tr/th')
    ]
    for row in parsed.xpath('//tbody/tr'):
        record = {
            headers[index]: clean_space(column.text)
            for index, column in enumerate(row)
            if clean_space(column.text)
        }
        record["iso"] = record["iso"].upper()
        yield CarrierDotCom(
            brand=record.get("network"),
            iso_code=record["iso"] if record["iso"] != "N/A" else None,
            plmn=PLMN.from_tuple(record["mcc"], record["mnc"]),
        )
