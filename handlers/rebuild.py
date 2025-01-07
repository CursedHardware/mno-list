import json
from typing import Type

from peewee import *

from .database import *
from .plmn import PLMN


def rebuild_carriers():
    db.drop_tables([Carrier])
    db.create_tables([Carrier])
    with db.atomic():
        Carrier.bulk_create(rebuild(CarrierDotNet, CarrierDotCom), batch_size=100)
        Carrier.bulk_create(rebuild(CarrierDotCom, CarrierDotNet), batch_size=100)


def export_carriers(type_carrier: Type[Carrier] = Carrier):
    carriers = (
        type_carrier
        .select(type_carrier.brand, type_carrier.operator)
        .group_by(type_carrier.brand, type_carrier.operator)
        .order_by(type_carrier.brand, type_carrier.operator)
    )
    for carrier in carriers:
        plmn_by_countries = (
            type_carrier
            .select(fn.ifnull(type_carrier.iso_code, "XX").alias("iso_code"),
                    fn.json_group_array(type_carrier.plmn).alias("plmn_array"))
            .where(type_carrier.brand == carrier.brand, type_carrier.operator == carrier.operator)
            .group_by(type_carrier.iso_code)
            .order_by(SQL("iso_code"))
        )
        yield {
            "brand": carrier.brand,
            "operator": carrier.operator,
            "mccmnc_tuple": {
                plmn.iso_code: list(sorted(set(map(PLMN.fromhex, json.loads(plmn.plmn_array)))))
                for plmn in plmn_by_countries
            }
        }


def rebuild(a: Type[Carrier], b: Type[Carrier]):
    carriers = (
        a.select(a.brand, a.operator, a.iso_code,
                 fn.json_group_array(a.plmn).alias("plmn_array"))
        .group_by(a.brand, a.operator, a.iso_code)
    )
    moved_plmn_set = set()
    for carrier in carriers:
        matched_plmn_set = {
            PLMN(bytes.fromhex(plmn))
            for plmn in json.loads(carrier.plmn_array)
        }
        matched_carrier = \
            (b.select(b.brand, b.operator, b.iso_code,
                      fn.json_group_array(b.plmn).alias("plmn_array"))
             .where(b.plmn.in_(matched_plmn_set))
             .group_by(b.brand, b.operator, b.iso_code)
             .order_by(fn.count("plmn_array").desc())
             .first())
        if matched_carrier:
            matched_plmn_set.update(
                PLMN(bytes.fromhex(plmn))
                for plmn in json.loads(matched_carrier.plmn_array)
            )
        for plmn in matched_plmn_set:
            yield Carrier(
                brand=carrier.brand,
                operator=carrier.operator,
                iso_code=carrier.iso_code,
                plmn=plmn,
            )
        moved_plmn_set.update(matched_plmn_set)
    a.delete().where(a.plmn.in_(moved_plmn_set)).execute()
    b.delete().where(b.plmn.in_(moved_plmn_set)).execute()
