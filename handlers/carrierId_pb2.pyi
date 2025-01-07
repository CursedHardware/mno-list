from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, \
    Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor


class CarrierList(_message.Message):
    __slots__ = ("carrier_id", "version")
    CARRIER_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    carrier_id: _containers.RepeatedCompositeFieldContainer[CarrierId]
    version: int

    def __init__(self, carrier_id: _Optional[_Iterable[_Union[CarrierId, _Mapping]]] = ...,
                 version: _Optional[int] = ...) -> None: ...


class CarrierId(_message.Message):
    __slots__ = ("canonical_id", "carrier_name", "carrier_attribute", "parent_canonical_id")
    CANONICAL_ID_FIELD_NUMBER: _ClassVar[int]
    CARRIER_NAME_FIELD_NUMBER: _ClassVar[int]
    CARRIER_ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
    PARENT_CANONICAL_ID_FIELD_NUMBER: _ClassVar[int]
    canonical_id: int
    carrier_name: str
    carrier_attribute: _containers.RepeatedCompositeFieldContainer[CarrierAttribute]
    parent_canonical_id: int

    def __init__(self, canonical_id: _Optional[int] = ..., carrier_name: _Optional[str] = ...,
                 carrier_attribute: _Optional[_Iterable[_Union[CarrierAttribute, _Mapping]]] = ...,
                 parent_canonical_id: _Optional[int] = ...) -> None: ...


class CarrierAttribute(_message.Message):
    __slots__ = ("mccmnc_tuple", "imsi_prefix_xpattern", "spn", "plmn", "gid1", "gid2", "preferred_apn", "iccid_prefix",
                 "privilege_access_rule")
    MCCMNC_TUPLE_FIELD_NUMBER: _ClassVar[int]
    IMSI_PREFIX_XPATTERN_FIELD_NUMBER: _ClassVar[int]
    SPN_FIELD_NUMBER: _ClassVar[int]
    PLMN_FIELD_NUMBER: _ClassVar[int]
    GID1_FIELD_NUMBER: _ClassVar[int]
    GID2_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_APN_FIELD_NUMBER: _ClassVar[int]
    ICCID_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PRIVILEGE_ACCESS_RULE_FIELD_NUMBER: _ClassVar[int]
    mccmnc_tuple: _containers.RepeatedScalarFieldContainer[str]
    imsi_prefix_xpattern: _containers.RepeatedScalarFieldContainer[str]
    spn: _containers.RepeatedScalarFieldContainer[str]
    plmn: _containers.RepeatedScalarFieldContainer[str]
    gid1: _containers.RepeatedScalarFieldContainer[str]
    gid2: _containers.RepeatedScalarFieldContainer[str]
    preferred_apn: _containers.RepeatedScalarFieldContainer[str]
    iccid_prefix: _containers.RepeatedScalarFieldContainer[str]
    privilege_access_rule: _containers.RepeatedScalarFieldContainer[str]

    def __init__(self, mccmnc_tuple: _Optional[_Iterable[str]] = ...,
                 imsi_prefix_xpattern: _Optional[_Iterable[str]] = ..., spn: _Optional[_Iterable[str]] = ...,
                 plmn: _Optional[_Iterable[str]] = ..., gid1: _Optional[_Iterable[str]] = ...,
                 gid2: _Optional[_Iterable[str]] = ..., preferred_apn: _Optional[_Iterable[str]] = ...,
                 iccid_prefix: _Optional[_Iterable[str]] = ...,
                 privilege_access_rule: _Optional[_Iterable[str]] = ...) -> None: ...
