from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class ObjectFile:
    original_filename: str
    extension: str
    filesize: int
    versions: dict

@dataclass_json
@dataclass
class InnerObject:
    file: List[ObjectFile]

@dataclass_json
@dataclass
class PluginDocument:
    object: InnerObject
    _uuid: str
    _system_object_id: str