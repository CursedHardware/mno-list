import os
import re
import tarfile
from collections import defaultdict
from io import BytesIO
from urllib.parse import urljoin

import requests
from lxml import etree

BRANCH = "refs/heads/main"

CARRIER_CONFIG_URL = urljoin(
    base="https://android.googlesource.com/platform/packages/apps/CarrierConfig/",
    url=os.path.join("+archive", BRANCH, "assets.tar.gz"),
)

RE_CARRIER_ID = re.compile(r"^carrier_config_carrierid_(?P<carrier_id>\d+)")


def fetch(session: requests.Session):
    for carrier_id, configs in load_carrier_configs(session).items():
        if len(configs) == 0:
            continue
        yield {
            "carrier_id": carrier_id,
            "carrier_config": configs[0] if len(configs) == 1 else configs,
        }


def load_carrier_configs(session: requests.Session):
    response = session.get(url=CARRIER_CONFIG_URL)
    response.raise_for_status()

    def parse_bundle(tree):
        bundle: dict[str, bool | int | list[int] | str | list[str]] = dict()

        def get_value(ele: etree.ElementBase) -> str:
            return ele.get("value") or ele.text

        def get_items(ele: etree.ElementBase) -> list[str]:
            return [item.get("value") or item.text for item in ele.iter("item")]

        for element in tree:
            element: etree.ElementBase
            field_name = element.get("name")
            if field_name is None:
                continue
            if element.tag == "boolean":
                bundle[field_name.removesuffix("_bool")] = get_value(element) == "true"
            elif element.tag == "int":
                bundle[field_name.removesuffix("_int")] = int(get_value(element))
            elif element.tag == "int-array":
                bundle[field_name.removesuffix("_int_array")] = list(map(int, get_items(element)))
            elif element.tag == "string":
                bundle[field_name.removesuffix("_string")] = get_value(element)
            elif element.tag == "string-array":
                bundle[field_name.removesuffix("_string_array")] = get_items(element)
        return bundle

    configs = defaultdict(list[dict])
    with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:
        for name in tar.getnames():
            matched = RE_CARRIER_ID.match(name)
            if not matched:
                continue

            carrier_id = int(matched.group("carrier_id"))
            root: etree.ElementBase = etree.fromstringlist(tar.extractfile(name))
            bundles: list[dict] = []
            if root.tag == "carrier_config":
                bundles = [parse_bundle(root)]
            elif root.tag == "carrier_config_list":
                bundles = [parse_bundle(config) for config in root.iter("carrier_config")]
            configs[carrier_id] = [bundle for bundle in bundles if bundle]
    return configs
