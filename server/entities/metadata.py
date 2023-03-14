from dataclasses import dataclass
from typing import Any, Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Metadata:
    schema_version: str
    metadata: dict[str, Any]
    resource_type: str
    id: Optional[str] = None
    url: Optional[str] = None

    @staticmethod
    def convert(metadata_in: dict[str, Any]) -> dict[str, Any]:
        metadata_out: Metadata = Metadata.from_dict(metadata_in) 
        metadata_out.id = metadata_in.get('_id')
        return metadata_out.to_dict() # type: ignore