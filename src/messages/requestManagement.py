import json

from spade.message import Message

from src.config import ONTOLOGY


class Response(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'user_requests', 'ontology': ONTOLOGY})


class Retrieve(Message):
    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'protocol': 'user_requests', 'ontology': ONTOLOGY})
