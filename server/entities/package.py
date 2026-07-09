import datetime
from dataclasses import dataclass, field
from typing import Any, Literal

from dataclasses_json import DataClassJsonMixin, config

from .archive_settings import ArchiveSettings

def shouldBeExcluded(x):
    return x is None

def in_three_days_milliseconds():
    return int((datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=3)).timestamp()*1000)

@dataclass
class Package(DataClassJsonMixin):
    name: str
    status: Literal["active", "archived", "review", "rework"]
    documents: list[str]
    folders: list[str]
    created: int
    last_changed: int
    owner: str
    organisation: str
    keep_until: int = field(default_factory=in_three_days_milliseconds) # set default value during migration
    owner_displayname: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    metadata: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    archive_id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    archive_settings: ArchiveSettings | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    reviews: list[str] | None = field(default=None, metadata=config(exclude=shouldBeExcluded))


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