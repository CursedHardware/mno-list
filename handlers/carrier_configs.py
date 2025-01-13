import os
import re
import tarfile
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
    for carrier_id, config in load_carrier_configs(session).items():
        if not config:
            continue
        yield {
            "carrier_id": carrier_id,
            "carrier_config": config,
        }

def load_carrier_configs(session: requests.Session):
    response = session.get(url=CARRIER_CONFIG_URL)
    response.raise_for_status()

    def parse_bundle(tree):
        bundle = dict()
        for element in tree:
            element: etree.ElementBase
            field_name = element.get("name")
            if field_name is None:
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
                if len(root) == 1:
                    configs[carrier_id] = parse_bundle(root[0])
                elif len(root) > 1:
                    configs[carrier_id] = [parse_bundle(config) for config in root.iter("carrier_config")]
    return configs
