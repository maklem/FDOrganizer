from typing import Any
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin 

@dataclass
class InnerCollection(DataClassJsonMixin):
    _id: str
    displayname: dict[str, Any]

@dataclass
class PluginFolder(DataClassJsonMixin):
    collection: InnerCollection
