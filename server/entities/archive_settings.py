from dataclasses import dataclass, field
from typing import Literal

from dataclasses_json import DataClassJsonMixin, config

shouldBeExcluded = lambda x: x is None


@dataclass
class ArchiveSettings(DataClassJsonMixin):
    findability: Literal['open', 'closed']
    licenseType: Literal['cc', 'gdl']
    licenseTiming: Literal['now', 'later']
    license: str
    checkDuration: bool
    duration: int
    checkTerms: bool
    checkDSGVO: bool
    personalData: Literal['none', 'anonymous', 'consent']
    contactemail: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    accessibility: Literal['open', 'embargo', 'request', 'closed'] | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    embargodate: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
