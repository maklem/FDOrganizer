from dataclasses import dataclass
from typing import Literal, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class File:
    name: str
    size: int
    mimetype: str
    is_stored: bool
    origin: Literal["manual"] | Literal["easyDB"]
    owner: str
    id: Optional[str] = None
    resource_type: Optional[str] = "Other"
    origin_id: Optional[str] = None
