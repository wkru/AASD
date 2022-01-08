import json

from spade.message import Message

from config import ONTOLOGY


class RegistrationRequest(Message):
    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'protocol': 'register', 'ontology': ONTOLOGY})


class DeregistrationRequest(Message):
    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'protocol': 'deregister', 'ontology': ONTOLOGY})