from dataclasses import dataclass, field
from typing import Any

from dataclasses_json import DataClassJsonMixin, config


def shouldBeExcluded(x):
    return x is None


@dataclass
class Document(DataClassJsonMixin):
    name: str
    size: int
    hash_md5: str
    hash_sha512: str
    type: str
    source: str
    owner: str
    id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    source_id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    metadata: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))

    @staticmethod
    def convert(document_in: dict[str, Any]) -> dict[str, Any]:
        document_out: Document = Document.from_dict(document_in) 
        document_out.id = document_in.get('_id')
        return document_out.to_dict()
    
    @staticmethod
    def from_db(document_in: dict[str, Any]) -> "Document":
        document_out: Document = Document.from_dict(document_in) 
        document_out.id = document_in.get('_id')
        return document_out
    
