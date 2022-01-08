import json

from spade.message import Message

from config import ONTOLOGY


class ServiceRetrieve(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'request', 'protocol': 'local_services_offers', 'ontology': ONTOLOGY})


class ServiceRespond(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'local_service_offers', 'ontology': ONTOLOGY})