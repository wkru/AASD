import json

from spade.message import Message

from config import ONTOLOGY


class OffersRetrieve(Message):
    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'protocol': 'vault_offers', 'ontology': ONTOLOGY})


class OffersResponse(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'response', 'protocol': 'vault_offers', 'ontology': ONTOLOGY})


class CategoriesRetrieve(Message):
    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'protocol': 'vault_categories', 'ontology': ONTOLOGY})


class CategoriesResponse(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'response', 'protocol': 'vault_categories', 'ontology': ONTOLOGY})


class AddProductRequest(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'request', 'protocol': 'vault_add', 'ontology': ONTOLOGY})


class GetProductRequest(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'request', 'protocol': 'vault_get', 'ontology': ONTOLOGY})


class GetProductResponse(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'response', 'protocol': 'vault_get', 'ontology': ONTOLOGY})

