from dataclasses import dataclass
from typing import Literal, Optional, Union
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class MetadataField:
    id: str
    label: Union[str, dict[str, str]]
    alias: list[str]
    type: Union[Literal["text"], Literal["decimal"], Literal["integer"], Literal["boolean"], Literal["monoselect"], Literal["date"], Literal["doi"], Literal["uri"],Literal["letter-string"]]
    fields: Optional[list['MetadataField']]
    min: Optional[int]
    max: Optional[int]
    options: Optional[list[dict[Union[Literal["id"], Literal["label"]], str]]]
    conditions: Optional[list[tuple[str, str, str]]]
    applicable: Optional[list[str]]
