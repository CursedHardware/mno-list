#!/usr/bin/env python3
import json
import os
from pathlib import Path

import cbor2
import msgpack
from peewee import SqliteDatabase
from requests import Session
from requests_cache import CachedSession

from handlers import google, mccmnc_dot_net, mccmnc_dot_com, mcc_table
from handlers.database import db
from handlers.rebuild import rebuild_carriers, export_carriers
from handlers.utils import CustomEncoder, emit_file

IS_CI = "CI" in os.environ
BASE_PATH = Path(os.getcwd())
DATA_PATH = BASE_PATH / "carriers"
NPM_PATH = BASE_PATH / "npm" / "carriers"


def main():
    session = Session() if IS_CI else CachedSession(".cache")
    db.initialize(SqliteDatabase(":memory:" if IS_CI else "plmn.sqlite"))
    with db, session:
        print("Downloading from mcc-mnc.net")
        mccmnc_dot_net.fetch(session)
        print("Downloading from mcc-mnc.com")
        mccmnc_dot_com.fetch(session)
        print("Rebuilding mcc-mnc.{com,net}")
        rebuild_carriers()
        print("Exporting mcc-mnc.{com,net}")
        save_file(list(export_carriers()), name="unified")
        print("Downloading from Google")
        save_file(list(google.fetch(session)), name="google")
        save_file(list(mcc_table.fetch(session)), name="mcc-table")



def save_file(carriers: list[dict[str, str]], name: str):
    emit_file(json.dumps(carriers, cls=CustomEncoder, indent=2), paths=[
        DATA_PATH / f"{name}.json",
    ])
    emit_file(json.dumps(carriers, cls=CustomEncoder), paths=[
        DATA_PATH / f"{name}.min.json",
        DATA_PATH / f"{name}.min.json.gz",
        DATA_PATH / f"{name}.min.json.bz2",
        NPM_PATH / f"{name}.json",
    ])
    emit_file(cbor2.dumps(carriers), paths=[
        DATA_PATH / f"{name}.cbor.gz",
        DATA_PATH / f"{name}.cbor.bz2",
    ])
    emit_file(msgpack.dumps(carriers), paths=[
        DATA_PATH / f"{name}.msgpack.gz",
        DATA_PATH / f"{name}.msgpack.bz2",
    ])


if __name__ == "__main__":
    main()
