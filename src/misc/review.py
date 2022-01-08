from dataclasses import dataclass


@dataclass
class ReviewToken:
    hash_: int


@dataclass
class Review:
    contents: str
    rating: int
    request_id: int
    from_: str
    to: str
