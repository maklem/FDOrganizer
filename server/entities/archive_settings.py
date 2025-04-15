from dataclasses import dataclass, field
from typing import Literal

from dataclasses_json import DataClassJsonMixin, config

shouldBeExcluded = lambda x: x is None


@dataclass
class ArchiveSettings(DataClassJsonMixin):
    checkDuration: bool
    duration: int
    checkTerms: bool
    checkDSGVO: bool
    personalData: Literal['none', 'anonymous', 'consent']
