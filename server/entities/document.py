from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Document:
    name: str
    size: int
    type: str
    is_stored: bool
    source: str
    owner: str
    id: Optional[str] = None
    source_id: Optional[str] = None
    metadata: Optional[str] = None
