from typing import Any
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class InnerCollection:
    _id: str
    displayname: dict[str, Any]

@dataclass_json
@dataclass
class PluginFolder:
    collection: InnerCollection
