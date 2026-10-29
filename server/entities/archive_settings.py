from dataclasses import dataclass
from typing import Literal

from dataclasses_json import DataClassJsonMixin

shouldBeExcluded = lambda x: x is None


@dataclass
class ArchiveSettings(DataClassJsonMixin):
    checkDuration: bool
    duration: int
    checkTerms: bool
    checkDSGVO: bool
    personalData: Literal["none", "anonymous", "consent"]
