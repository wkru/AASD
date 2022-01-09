from dataclasses import dataclass


class ReviewToken:
    def __init__(self, request_id: int, user_ids: list):
        self.request_id = request_id
        self.hash_ = hash(str(request_id) + str(user_ids))

    def __eq__(self, other):
        return self.hash_ == other.hash_

    @classmethod
    def from_dict(cls, dct):
        token = cls(0, [])
        token.__dict__ = dct
        return token


@dataclass
class Review:
    contents: str
    rating: int
    request_id: int
    from_: str
    to: str
