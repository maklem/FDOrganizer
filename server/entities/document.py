from dataclasses import dataclass
from typing import Literal, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Document:
    name: str
    size: int
    mimetype: str
    is_stored: bool
    origin: Literal["manual"] | str
    owner: str
    _id: Optional[str] = None
    source_id: Optional[str] = None
    resource_type: Optional[str] = "Other"
    metadata: Optional[str] = None
