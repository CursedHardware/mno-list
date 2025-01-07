from peewee import CharField

from ..plmn import PLMN


class PLMNField(CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(max_length=6, *args, **kwargs)

    def db_value(self, value):
        if isinstance(value, PLMN):
            return value.hex()
        raise ValueError(f"Expected PLMN, got {value}")

    def python_value(self, value):
        if isinstance(value, str):
            return PLMN(bytes.fromhex(value))
        raise ValueError(f"Expected PLMN, got {value}")
