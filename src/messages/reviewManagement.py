import json

from spade.message import Message

from config import ONTOLOGY


class Leaderboard(Message):
    metadata = {'performative': 'request', 'protocol': 'review-collector-leaderboard', 'ontology': ONTOLOGY}

    def __init__(self, to):
        super().__init__(to=to, metadata=self.metadata)


class LeaderboardResponse(Message):
    metadata = {'performative': 'inform', 'protocol': 'review-collector-leaderboard'}

    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata=self.metadata)
