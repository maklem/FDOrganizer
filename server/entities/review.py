from dataclasses import dataclass, field
from typing import Any, Literal
from dataclasses_json import DataClassJsonMixin, config

from .comment import Comment


shouldBeExcluded = lambda x: x is None

@dataclass
class Review(DataClassJsonMixin):
    package_id: str
    status: Literal["open", "accepted", "rejected"]
    comments: list[Comment]
    creation_date: int | None = field(default=None, metadata=config(exclude=shouldBeExcluded))
    id: str | None = field(default=None, metadata=config(exclude=shouldBeExcluded))

    @staticmethod
    def convert(review_in: dict[str, Any]) -> dict[str, Any]:
        review_out: Review = Review.from_dict(review_in)
        review_out.id = review_in.get('_id')
        return review_out.to_dict()
    
    @staticmethod
    def from_db(review_in: dict[str, Any]) -> "Review":
        review_out: Review = Review.from_dict(review_in)
        review_out.id = review_in.get('_id')
        return review_out