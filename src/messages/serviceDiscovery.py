import json

from spade.message import Message

from config import ONTOLOGY


class ServicesRetrieve(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'request', 'protocol': 'local_services', 'ontology': ONTOLOGY})


class ServicesRespond(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'local_services', 'ontology': ONTOLOGY})