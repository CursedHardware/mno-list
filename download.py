#!/usr/bin/env python3
import json
import os

import cbor2
import msgpack
from peewee import SqliteDatabase
from requests import Session
from requests_cache import CachedSession

from handlers import google, mccmnc_dot_net, mccmnc_dot_com
from handlers.database import db
from handlers.rebuild import rebuild_carriers, export_carriers
from handlers.utils import CustomEncoder, emit_file

IS_CI = "CI" in os.environ


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


def save_file(carriers: list[dict[str, str]], name: str):
    emit_file(json.dumps(carriers, cls=CustomEncoder, indent=2), filenames=[
        os.path.join("carriers", f"{name}.json"),
    ])
    emit_file(json.dumps(carriers, cls=CustomEncoder), filenames=[
        os.path.join("carriers", f"{name}.min.json"),
        os.path.join("npm", "carriers", f"{name}.json"),
    ])
    emit_file(cbor2.dumps(carriers), filenames=[
        os.path.join("carriers", f"{name}.cbor.gz"),
    ])
    emit_file(msgpack.dumps(carriers), filenames=[
        os.path.join("carriers", f"{name}.msgpack.gz"),
    ])


if __name__ == "__main__":
    main()
