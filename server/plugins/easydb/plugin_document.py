from typing import List
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin 

@dataclass
class ObjectFile(DataClassJsonMixin):
    original_filename: str
    extension: str
    filesize: int
    versions: dict

@dataclass
class InnerObject(DataClassJsonMixin):
    file: List[ObjectFile]

@dataclass
class PluginDocument(DataClassJsonMixin):
    object: InnerObject
    _uuid: str
    _system_object_id: str