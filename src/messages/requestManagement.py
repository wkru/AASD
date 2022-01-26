import json

from spade.message import Message

from src.config import ONTOLOGY


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
        super().__init__(to=to, body=body, metadata={'performative': 'propagate', 'protocol': 'addition', 'ontology': ONTOLOGY})


class BroadcastNew(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'propagate', 'protocol': 'addition', 'ontology': ONTOLOGY})


class Acceptance(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'proxy', 'protocol': 'acceptance', 'ontology': ONTOLOGY})


class AcceptanceForward(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'acceptance', 'ontology': ONTOLOGY})


class Cancellation(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body,
                         metadata={'performative': 'propagate', 'protocol': 'cancellation', 'ontology': ONTOLOGY})


class CancellationForward(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body,
                         metadata={'performative': 'propagate', 'protocol': 'cancellation', 'ontology': ONTOLOGY})

class CategoriesRetrieve(Message):
    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'protocol': 'categories', 'ontology': ONTOLOGY})


class CategoriesResponse(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'categories', 'ontology': ONTOLOGY})


class UserListRetrieve(Message):
    metadata = {'performative': 'request', 'protocol': 'user_list'}

    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'protocol': 'user_list', 'ontology': ONTOLOGY})


class UserListResponse(Message):
    metadata = {'performative': 'inform', 'protocol': 'user_list'}

    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'protocol': 'user_list', 'ontology': ONTOLOGY})
