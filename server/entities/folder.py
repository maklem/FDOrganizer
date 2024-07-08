from dataclasses import dataclass, field
from typing import Any

from dataclasses_json import DataClassJsonMixin, config

shouldBeExcluded = lambda x: x is None

@dataclass
class Folder(DataClassJsonMixin):
    name: str
    owner: str
    folders: list[str]
    documents: list[str]
    id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    metadata: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))

    @staticmethod
    def convert(folder_in: dict[str, Any]) -> dict[str, Any]:
        folder_out: Folder = Folder.from_dict(folder_in)
        folder_out.id = folder_in.get('_id')
        return folder_out.to_dict()
