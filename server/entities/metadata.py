from dataclasses import dataclass, field
from typing import Any
from dataclasses_json import DataClassJsonMixin, config

shouldBeExcluded = lambda x: x is None

@dataclass
class Metadata(DataClassJsonMixin):
    schema_version: str
    metadata: dict[str, Any]
    id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    url: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))

    @staticmethod
    def convert(metadata_in: dict[str, Any]) -> dict[str, Any]:
        metadata_out: Metadata = Metadata.from_dict(metadata_in) 
        metadata_out.id = metadata_in.get('_id')
        return metadata_out.to_dict()