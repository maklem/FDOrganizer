from dataclasses import dataclass
from typing import Literal, Optional, Union

from dataclasses_json import dataclass_json



@dataclass_json
@dataclass
class ArchiveSettings:
    findability: Union[Literal['open'], Literal['closed']]
    licenseType: Union[Literal['cc'], Literal['gdl']]
    licenseTiming: Union[Literal['now'], Literal['later']]
    license: str
    checkDuration: bool
    duration: int
    checkTerms: bool
    checkDSGVO: bool
    personalData: Union[Literal['none'], Literal['anonymous'], Literal['consent']]
    contactemail: Optional[str] = None
    accessibility: Optional[Union[Literal['open'], Literal['embargo'], Literal['request'], Literal['closed']]] = None
    embargodate: Optional[str] = None
