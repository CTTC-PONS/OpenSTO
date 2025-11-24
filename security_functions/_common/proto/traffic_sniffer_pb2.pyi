from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNKNOWN: _ClassVar[StatusEnum]
    STATUS_STOPPED: _ClassVar[StatusEnum]
    STATUS_RUNNING: _ClassVar[StatusEnum]
STATUS_UNKNOWN: StatusEnum
STATUS_STOPPED: StatusEnum
STATUS_RUNNING: StatusEnum

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Configuration(_message.Message):
    __slots__ = ("source_interface", "capture_filter")
    SOURCE_INTERFACE_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_FILTER_FIELD_NUMBER: _ClassVar[int]
    source_interface: str
    capture_filter: str
    def __init__(self, source_interface: _Optional[str] = ..., capture_filter: _Optional[str] = ...) -> None: ...

class Status(_message.Message):
    __slots__ = ("status", "detail")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    status: StatusEnum
    detail: str
    def __init__(self, status: _Optional[_Union[StatusEnum, str]] = ..., detail: _Optional[str] = ...) -> None: ...
