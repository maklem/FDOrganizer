from dataclasses import dataclass
from typing import Literal


@dataclass
class CouchDocument:
    id: str
    rev: str

    def __init__(self, document_response: dict[Literal['id', 'rev'], str]):
        self.id = document_response['id']
        self.rev = document_response['rev']
