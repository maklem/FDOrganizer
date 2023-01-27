from dataclasses import dataclass
from typing import Any, Optional

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

    @staticmethod
    def convert(document_in: dict[str, Any]) -> dict[str, Any]:
        document_out: Document = Document.from_dict(document_in) 
        document_out.id = document_in.get('_id')
        return document_out.to_dict() # type: ignore
