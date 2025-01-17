import base64
import os
from urllib.parse import urljoin

import requests

from .carrierId_pb2 import CarrierList, CarrierAttribute
from .plmn import PLMN
from .utils import clean_space

BRANCH = "HEAD"

CARRIER_LIST_URL = urljoin(
    base="https://android.googlesource.com/platform/packages/providers/TelephonyProvider/",
    url=os.path.join("+", BRANCH, "assets/latest_carrier_id/carrier_list.pb"),
)



def fetch(session: requests.Session):
    return load_carrier_ids(session)


def load_carrier_ids(session: requests.Session) -> list[dict]:
    response = session.get(url=CARRIER_LIST_URL, params={"format": "TEXT"})
    response.raise_for_status()

    carriers = CarrierList()
    carriers.ParseFromString(base64.decodebytes(response.content))

    for carrier_id in carriers.carrier_id:
        yield {
            "canonical_id": carrier_id.canonical_id,
            "parent_canonical_id": carrier_id.parent_canonical_id,
            "carrier_name": clean_space(carrier_id.carrier_name),
            "carrier_attribute": list(map(attribute_from_pb2, carrier_id.carrier_attribute)),
        }


def attribute_from_pb2(carrier_attribute: CarrierAttribute) -> dict:
    attributes: dict[str, list[str | bytes]] = {
        desc.name: list(sorted(value for value in values if len(value) > 0))
        for desc, values in carrier_attribute.ListFields()
    }
    attributes: dict[str, list[str | bytes]] = {
        name: values
        for name, values in attributes.items()
        if len(values) > 0
    }

    def handle_plmn(name: str):
        values = attributes.get(name)
        if not values:
            return
        attributes[name] = list(map(PLMN.from_mccmnc_tuple, values))

    def handle_hex(name: str):
        values = attributes.get(name)
        if not values:
            return
        attributes[name] = [
            bytes.fromhex(value)
            for value in values
            if len(value) % 2 == 0
        ]

    handle_plmn("mccmnc_tuple")
    handle_hex("gid1")
    handle_hex("gid2")
    handle_hex("privilege_access_rule")
    return attributes
