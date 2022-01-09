from dataclasses import dataclass


class ReviewToken:
    def __init__(self, request_id: int, user_ids: list):
        self.hash_ = hash(str(request_id) + str(user_ids))

    def __eq__(self, other):
        return self.hash_ == other.hash_


@dataclass
class Review:
    contents: str
    rating: int
    request_id: int
    from_: str
    to: str
