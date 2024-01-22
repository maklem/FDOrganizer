from dataclasses import dataclass, field
from typing import Literal, Optional, Union, Any
from dataclasses_json import config, dataclass_json

@dataclass_json
@dataclass
class IdentityProvider:
    type: Literal["SAML", "OIDC", "LDAP"]
    url: str
    scope: list[str]
    client_id: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))
    client_secret: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))

@dataclass_json
@dataclass
class Organisation:
    name: str
    reviewers: list[str]
    # rosetta_token: str
    plugins: list[str]
    identity_provider: IdentityProvider
    id: Optional[str] = field(default=None, metadata=config(exclude=lambda x: x is None))

    @staticmethod
    def from_db(organisation_in: dict[str, Any]) -> "Organisation":
        organisation_out: Organisation = Organisation.from_dict(organisation_in)
        organisation_out.id = organisation_in.get('_id')
        return organisation_out