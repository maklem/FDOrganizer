from dataclasses import dataclass, field
from typing import Any
from dataclasses_json import DataClassJsonMixin, config

shouldBeExcluded = lambda x: x is None
@dataclass
class Comment(DataClassJsonMixin):
    index: int
    content: str
    owner: str
    file_reference: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))


    @staticmethod
    def convert(comment_in: dict[str, Any]) -> dict[str, Any]:
        comment_out: Comment = Comment.from_dict(comment_in)
        return comment_out.to_dict()
    
    @staticmethod
    def from_db(comment_in: dict[str, Any]) -> "Comment":
        comment_out: Comment = Comment.from_dict(comment_in)
        return comment_out