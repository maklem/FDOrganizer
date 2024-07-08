from dataclasses import dataclass
from typing import Literal
from dataclasses_json import DataClassJsonMixin


@dataclass
class MetadataField(DataClassJsonMixin):
    id: str
    label: str | dict[str, str]
    alias: list[str]
    type: Literal["text", "decimal", "integer", "boolean", "monoselect", "date", "doi", "uri", "letter-string", "orcid", "ror", "ddc", "wikidata", "latitude", "longitude"]
    fields: list['MetadataField'] | None
    min: int | None
    max: int | None
    options: list[dict[Literal["id", "label"], str]] | None
    conditions: list[tuple[str, str, str]] | None
    applicable: list[str] | None
