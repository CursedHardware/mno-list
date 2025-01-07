from peewee import *

from .fields import PLMNField

db = DatabaseProxy()

PLMNThroughModel = DeferredThroughModel()


class BaseModel(Model):
    class Meta:
        database = db


class Carrier(BaseModel):
    class Meta:
        indexes = (
            (("brand", "operator", "iso_code", "plmn"), True),
        )

    id = PrimaryKeyField()
    brand = CharField(null=True, constraints=[SQL('COLLATE NOCASE')])
    operator = CharField(null=True, constraints=[SQL('COLLATE NOCASE')])
    iso_code = CharField(null=True, constraints=[SQL('COLLATE NOCASE')])
    plmn = PLMNField()


class CarrierDotCom(Carrier):
    pass


class CarrierDotNet(Carrier):
    pass
