from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional, Union

from dataclasses_json import dataclass_json, config

from .archive_settings import ArchiveSettings

@dataclass_json
@dataclass
class Package:
    name: str
    status: Literal["active", "archived"]
    documents: List[str]
    folders: List[str]
    created: int
    last_changed: int
    owner: str
    metadata: Optional[str] = field(default=None, metadata=config(exclude=lambda x: x is None))
    id: Optional[str] = field(default=None, metadata=config(exclude=lambda x: x is None))
    archive_id: Optional[str] = field(default=None, metadata=config(exclude=lambda x: x is None))
    archive_settings: Optional[ArchiveSettings] = field(default=None, metadata=config(exclude=lambda x: x is None))

    @staticmethod
    def convert(package_in: dict[str, Any]) -> dict[str, Any]:
        package_out: Package = Package.from_dict(package_in)
        package_out.id = package_in.get('_id')
        return package_out.to_dict()
    
    @staticmethod
    def from_db(package_in: dict[str, Any]) -> "Package":
        package_out: Package = Package.from_dict(package_in)
        package_out.id = package_in.get('_id')
        return package_out