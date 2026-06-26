from dataclasses import dataclass, field
from typing import Any
from dataclasses_json import DataClassJsonMixin, config

def shouldBeExcluded(x) -> bool:
    return x is None

@dataclass
class Organisation(DataClassJsonMixin):
    name: str
    reviewers: list[str]
    plugins: list[str]
    export_subdirectory: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    idp_id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))

    @staticmethod
    def from_db(organisation_in: dict[str, Any]) -> "Organisation":
        organisation_out: Organisation = Organisation.from_dict(organisation_in)
        organisation_out.id = organisation_in.get('_id')
        return organisation_out