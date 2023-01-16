from dataclasses import dataclass, field
from typing import List, Literal, Optional

from dataclasses_json import dataclass_json, config



@dataclass_json
@dataclass
class Package:
    name: str
    status: Literal["active"] | Literal["archived"]
    documents: List[str]
    folders: List[str]
    created: int
    last_changed: int
    owner: str
    metadata: Optional[str] = None
    id: Optional[str] = field(default=None, metadata=config(exclude=lambda x: x is None))
    archive_id: Optional[str] = None