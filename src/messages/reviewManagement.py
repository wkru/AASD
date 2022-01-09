import json

from spade.message import Message

from src.config import ONTOLOGY
from src.misc.review import Review, ReviewToken as Token


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


class ReviewCreation(Message):
    metadata = {'performative': 'request', 'protocol': 'review-collector-review-creation'}

    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata=dict(self.metadata, **{'ontology': ONTOLOGY}))


class ReviewTokenCreation(Message):
    metadata = {'performative': 'request', 'protocol': 'information-broker-review-token-creation'}

    def __init__(self, to: str, request_id: int, user_ids: list):
        body = json.dumps({'request_id': request_id, 'user_ids': user_ids})
        super().__init__(to=to, body=body, metadata=dict(self.metadata, **{'ontology': ONTOLOGY}))


class ReviewToken(Message):
    metadata = {'performative': 'inform', 'protocol': 'review-collector-receive-token'}

    def __init__(self, to, token: Token):
        body = json.dumps(token.__dict__)
        super().__init__(to=to, body=body, metadata=dict(self.metadata, **{'ontology': ONTOLOGY}))

