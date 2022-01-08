import json

from spade.message import Message

from config import ONTOLOGY
from misc.review import Review


class Leaderboard(Message):
    metadata = {'performative': 'request', 'protocol': 'review-collector-leaderboard'}

    def __init__(self, to):
        super().__init__(to=to, metadata=dict(self.metadata, **{'ontology': ONTOLOGY}))


class LeaderboardResponse(Message):
    metadata = {'performative': 'inform', 'protocol': 'review-collector-leaderboard'}

    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata=dict(self.metadata, **{'ontology': ONTOLOGY}))


class Reviews(Message):
    metadata = {'performative': 'request', 'protocol': 'review-collector-reviews'}

    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata=dict(self.metadata, **{'ontology': ONTOLOGY}))


class ReviewsResponse(Message):
    metadata = {'performative': 'inform', 'protocol': 'review-collector-reviews'}

    def __init__(self, to, data):
        body = json.dumps(data, default=lambda o: o.__dict__ if isinstance(o, Review) else o)
        super().__init__(to=to, body=body, metadata=dict(self.metadata, **{'ontology': ONTOLOGY}))
