from dataclasses import dataclass, field
from typing import Literal, Any
from dataclasses_json import DataClassJsonMixin, config

def shouldBeExcluded(x) -> bool:
    return x is None

@dataclass
class IdentityProvider(DataClassJsonMixin):
    type: Literal["LOCAL", "OIDC", "KEYCLOAK"]
    url: str
    scope: list[str]
    client_id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    client_secret: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    username_field: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    required_fields: dict[str,str] | None = field(default=None, metadata=config(exclude=shouldBeExcluded))

@dataclass
class Organisation(DataClassJsonMixin):
    name: str
    reviewers: list[str]
    plugins: list[str]
    identity_provider: IdentityProvider
    export_subdirectory: str
    id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))

    @staticmethod
    def from_db(organisation_in: dict[str, Any]) -> "Organisation":
        organisation_out: Organisation = Organisation.from_dict(organisation_in)
        organisation_out.id = organisation_in.get('_id')
        return organisation_out