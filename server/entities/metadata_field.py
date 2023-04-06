from dataclasses import dataclass
from typing import Literal, Optional, Union
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class MetadataField:
    id: str
    label: Union[str, dict[str, str]]
    alias: list[str]
    type: Literal["text", "decimal", "integer", "boolean", "monoselect", "date", "doi", "uri", "letter-string", "orcid", "ror", "ddc", "wikidata", "latitude", "longitude"]
    fields: Optional[list['MetadataField']]
    min: Optional[int]
    max: Optional[int]
    options: Optional[list[dict[Literal["id", "label"], str]]]
    conditions: Optional[list[tuple[str, str, str]]]
    applicable: Optional[list[str]]
