import base64
import os
import re
import tarfile
from io import BytesIO
from urllib.parse import urljoin

import requests
from lxml import etree

from .carrierId_pb2 import CarrierList, CarrierAttribute
from .plmn import PLMN
from .utils import clean_space

BRANCH = "refs/heads/main"

CARRIER_LIST_URL = urljoin(
    base="https://android.googlesource.com/platform/packages/providers/TelephonyProvider/",
    url=os.path.join("+", BRANCH, "assets/latest_carrier_id/carrier_list.pb"),
)

CARRIER_CONFIG_URL = urljoin(
    base="https://android.googlesource.com/platform/packages/apps/CarrierConfig/",
    url=os.path.join("+archive", BRANCH, "assets.tar.gz"),
)

RE_CARRIER_ID = re.compile(r"^carrier_config_carrierid_(?P<carrier_id>\d+)")


def fetch(session: requests.Session):
    configs = load_carrier_configs(session)
    return load_carrier_ids(session, configs)


def load_carrier_configs(session: requests.Session):
    response = session.get(url=CARRIER_CONFIG_URL)
    response.raise_for_status()

    def parse_bundle(tree):
        bundle = dict()
        for element in tree:
            element: etree.ElementBase
            field_name = element.get("name")
            if not field_name:
                continue
            field_name = field_name.removesuffix("_" + element.tag.replace("-", "_"))
            if element.tag == "boolean":
                field_name = field_name.removesuffix("_bool")
                bundle[field_name] = element.get("value") == "true"
            elif element.tag == "int":
                field_name = field_name.removesuffix("_int")
                bundle[field_name] = int(element.get("value"))
            elif element.tag == "int-array":
                field_name = field_name.removesuffix("_int_array")
                bundle[field_name] = [int(item.get("value")) for item in element.iter("item")]
            elif element.tag == "string":
                field_name = field_name.removesuffix("_string")
                bundle[field_name] = element.get("value") or element.text
            elif element.tag == "string-array":
                field_name = field_name.removesuffix("_string_array")
                bundle[field_name] = [item.get("value") for item in element.iter("item")]
        return bundle

    configs: dict[int, list[dict] | dict] = {}
    with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:
        for name in tar.getnames():
            matched = RE_CARRIER_ID.match(name)
            if not matched:
                continue

            carrier_id = int(matched.group("carrier_id"))
            root: etree.ElementBase = etree.fromstringlist(tar.extractfile(name))
            if root.tag == "carrier_config":
                configs[carrier_id] = parse_bundle(root)
            elif root.tag == "carrier_config_list":
                configs[carrier_id] = [parse_bundle(config) for config in root.iter("carrier_config")]
    return configs


def load_carrier_ids(session: requests.Session, configs: dict[int, list[dict]]) -> list[dict]:
    response = session.get(url=CARRIER_LIST_URL, params={"format": "TEXT"})
    response.raise_for_status()

    carriers = CarrierList()
    carriers.ParseFromString(base64.decodebytes(response.content))

    for carrier_id in carriers.carrier_id:
        record = {
            "canonical_id": carrier_id.canonical_id,
            "parent_canonical_id": carrier_id.parent_canonical_id,
            "carrier_name": clean_space(carrier_id.carrier_name),
            "carrier_attribute": list(map(attribute_from_pb2, carrier_id.carrier_attribute)),
        }
        if carrier_config := configs.get(carrier_id.canonical_id):
            record["carrier_config"] = carrier_config
        yield record


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
