from dataclasses import dataclass
from typing import Literal, Optional

from dataclasses_json import dataclass_json



@dataclass_json
@dataclass
class ArchiveSettings:
    findability: Literal['open', 'closed']
    licenseType: Literal['cc', 'gdl']
    licenseTiming: Literal['now', 'later']
    license: str
    checkDuration: bool
    duration: int
    checkTerms: bool
    checkDSGVO: bool
    personalData: Literal['none', 'anonymous', 'consent']
    contactemail: Optional[str] = None
    accessibility: Optional[Literal['open', 'embargo', 'request', 'closed']] = None
    embargodate: Optional[str] = None
