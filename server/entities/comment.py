from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, config

shouldBeExcluded = lambda x: x is None
@dataclass
class Comment(DataClassJsonMixin):
    index: str
    content: str
    owner: str
    file_reference: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))