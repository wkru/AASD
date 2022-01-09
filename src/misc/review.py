from dataclasses import dataclass


class Token:
    def __init__(self, request_id: int, from_: str, to: str):
        self.request_id = request_id
        self.from_ = from_
        self.to = to
        self.hash_ = hash(str(request_id) + str(from_) + str(to))

    def __eq__(self, other):
        if other is None:
            return False
        return self.hash_ == other.hash_

    @classmethod
    def from_dict(cls, dct):
        token = cls(0, '', '')
        token.__dict__ = dct
        return token


@dataclass
class Review:
    contents: str
    rating: int
    request_id: int
    from_: str
    to: str
