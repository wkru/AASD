import json

from spade.message import Message

from config import ONTOLOGY


class ListResponse(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'user_requests', 'ontology': ONTOLOGY})


class ListRetrieve(Message):
    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'protocol': 'user_requests', 'ontology': ONTOLOGY})


class Addition(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'request', 'protocol': 'addition', 'ontology': ONTOLOGY})


class BroadcastNew(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'addition', 'ontology': ONTOLOGY})


class Acceptance(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'request', 'protocol': 'acceptance', 'ontology': ONTOLOGY})


class AcceptanceForward(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'acceptance', 'ontology': ONTOLOGY})


class Cancellation(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body,
                         metadata={'performative': 'request', 'protocol': 'cancellation', 'ontology': ONTOLOGY})


class CancellationForward(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body,
                         metadata={'performative': 'inform', 'protocol': 'cancellation', 'ontology': ONTOLOGY})





