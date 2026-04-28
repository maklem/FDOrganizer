from dataclasses import dataclass, field
from typing import Literal, Any
from dataclasses_json import DataClassJsonMixin, config

def isNone(x) -> bool:
    return x is None

@dataclass
class IdentityProvider(DataClassJsonMixin):
    type: Literal["LOCAL", "OIDC", "KEYCLOAK"]
    name: str
    url: str
    scope: list[str]
    client_id: str | None = field(default=None, metadata=config(exclude=isNone))
    client_secret: str | None = field(default=None, metadata=config(exclude=isNone))
    username_field: str | None = field(default=None, metadata=config(exclude=isNone))
    displayname_field: str | None = field(default=None, metadata=config(exclude=isNone))
    organisation_field: str | None = field(default=None, metadata=config(exclude=isNone))
    organisation: str | None = field(default=None, metadata=config(exclude=isNone))
    id: str | None = field(default=None, metadata=config(exclude=isNone))

    @staticmethod
    def from_db(idp_data: dict[str, Any]) -> "IdentityProvider":
        idp_out: IdentityProvider = IdentityProvider.from_dict(idp_data)
        idp_out.id = idp_data.get('_id')
        return idp_out