import json

from spade.message import Message

from config import ONTOLOGY


class RegistrationRequest(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'request', 'protocol': 'user_add', 'ontology': ONTOLOGY})


class RegistrationRespond(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'user_get', 'ontology': ONTOLOGY})