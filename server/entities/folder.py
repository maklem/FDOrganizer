from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Folder:
    name: str
    owner: str
    folders: List[int]
    documents: List[int]
    id: Optional[str] = None
    metadata: Optional[str] = None
