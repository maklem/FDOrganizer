from dataclasses import dataclass
from typing import Any, List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Folder:
    name: str
    owner: str
    folders: List[str]
    documents: List[str]
    id: Optional[str] = None
    metadata: Optional[str] = None

    @staticmethod
    def convert(folder_in: dict[str, Any]) -> dict[str, Any]:
        folder_out: Folder = Folder.from_dict(folder_in)
        folder_out.id = folder_in.get('_id')
        return folder_out.to_dict() # type: ignore
