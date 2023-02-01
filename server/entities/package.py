from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional, Union

from dataclasses_json import dataclass_json, config



@dataclass_json
@dataclass
class Package:
    name: str
    status: Union[Literal["active"], Literal["archived"]]
    documents: List[str]
    folders: List[str]
    created: int
    last_changed: int
    owner: str
    metadata: Optional[str] = None
    id: Optional[str] = field(default=None, metadata=config(exclude=lambda x: x is None))
    archive_id: Optional[str] = None

    @staticmethod
    def convert(package_in: dict[str, Any]) -> dict[str, Any]:
        package_out: Package = Package.from_dict(package_in)
        package_out.id = package_in.get('_id')
        return package_out.to_dict()